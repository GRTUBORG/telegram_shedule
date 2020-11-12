import telebot
import datetime
import json
import os
import time

from telebot import types
from haversine import haversine, Unit
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.utils.config import get_default_config


token = os.environ.get('bot_token')
bot = telebot.TeleBot(str(token))
print('Бот работает!')
delta = datetime.timedelta(hours = 3, minutes = 0)
call_data = ["stations_1", "stations_2", "back_stations1", "back_stations2"]

@bot.message_handler(commands = ['start'])
def send_welcome(message):
    t = datetime.datetime.now(datetime.timezone.utc) + delta
    nowtime = t.strftime("%X")
    bot.send_message(655041562, 'У тебя +1 новый пользователь!')
    bot.reply_to(message, f'Привет! Текущее время: {nowtime}. Чтобы узнать расписание — пропиши команду (или нажми на неё) /schedule')
@bot.message_handler(commands = ['help'])
def send_help(message):
    bot.reply_to(message, "Привет! Рад, что ты заглянул(а) сюда :) \n1) /schedule - узнать расписание; \n2) /info - расстояние до ближайшей остановки; \n3) /back - возвращение в основное меню; \nТакже будем очень благодарны за поддержку проекта: /donations.")
@bot.message_handler(commands = ['schedule', 'back'])
def switch(message):
    config_dict = get_default_config()
    config_dict['language'] = 'ru'
    owm = OWM('0d16f6ffb7d46c30c1202a765e2cb0fc', config_dict)
    mgr = owm.weather_manager()
    observation = mgr.weather_at_place('Тейково')
    w = observation.weather
    temp = w.temperature('celsius')['temp']
    temperature = str(temp).rsplit(".")[0]
    if temperature == "-0":
        temperature = "0"
    t = datetime.datetime.now(datetime.timezone.utc) + delta
    nowtime = t.strftime("%d.%m.%Y, %X")
    nowtime_night = t.strftime("%X")
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    route1_button = types.KeyboardButton(text = "Узнать расписание для маршрута №1")
    route2_button = types.KeyboardButton(text = "Узнать расписание для маршрута №2")
    callback_button = types.KeyboardButton(text = "⬅️ В главное меню")
    stations_button = types.KeyboardButton(text = "Ближайшие остановки")
    donations_button = types.KeyboardButton(text = "Поддержать проект")
    if nowtime_night > '22:00:00' or nowtime_night < '04:45:00':
        keyboard.add(stations_button, donations_button, callback_button)
        bot.send_message(message.chat.id, f"*Главное меню* \n\nНа дворе: `{nowtime}`. \nВ Тейково *{temperature}°*. \n\nК сожалению, ночных рейсов пока что нет. Просьба подождать до первого рейса (`5:30` утра). \nСпасибо за понимание!", parse_mode = 'Markdown', reply_markup = keyboard)
    else:
        keyboard.add(route1_button, route2_button, stations_button, donations_button, callback_button)
        bot.send_message(message.chat.id, f"*Главное меню* \n\nНа дворе: `{nowtime}`. \nВ Тейково *{temperature}°*. \n\nВоспользуйся клавиатурой ниже, чтобы использовать функции бота!", parse_mode = 'Markdown', reply_markup = keyboard)
@bot.message_handler(commands = ['donations'])
def donations(message):
    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    url_button_qiwi = types.InlineKeyboardButton(text = "Поддержать: QIWI Кошелёк", url = "qiwi.com/n/OVERFLOW16")
    url_button_yandex = types.InlineKeyboardButton(text = "Поддержать: Яндекс.Деньги", url = "money.yandex.ru/to/410015133921329")
    keyboard.add(url_button_qiwi, url_button_yandex)
    bot.send_message(message.chat.id, "Я надеюсь, что этот бот тебе полезен, и очень буду признателен за поддержку нашего проекта! 😊", reply_markup = keyboard)
@bot.message_handler(commands = ["info"])
def geophone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    button_geo = types.KeyboardButton(text = "Отправить местоположение", request_location = True)
    callback_button = types.KeyboardButton(text = "⬅️ В главное меню")
    keyboard.add(button_geo, callback_button)
    bot.send_message(message.chat.id, "Отправь мне своё местоположение, чтобы узнать список остановок поблизости.", reply_markup = keyboard)  
@bot.message_handler(content_types = ['location'])
def handle_loc(message):
    data_loads_previous = json.load(open('./координаты_остановок.json'))
    data_previous = json.dumps(data_loads_previous)
    json_data_previous = json.loads(data_previous)
    route1_previous = json_data_previous["Маршрут №1"]
    route2_previous = json_data_previous["Маршрут №2"]
    key_1 = 0
    key_2 = 0
    quantity = 0
    while key_1 < 23:
        key_1 = str(key_1)
        coordinates_stations_1 = route1_previous.get(key_1)
        key_1 = int(key_1)
        key_1 += 1
        user_location_correct = (message.location.latitude, message.location.longitude)
        coordinates_stations_correct_1 = (coordinates_stations_1[0], coordinates_stations_1[1])
        distance1 = haversine(user_location_correct, coordinates_stations_correct_1, unit = 'm')
        if int(distance1) < 250:
            quantity += 1
    while key_2 < 17:
        key_2 = str(key_2)
        coordinates_stations_2 = route2_previous.get(key_2)
        key_2 = int(key_2)
        key_2 += 1
        user_location_correct = (message.location.latitude, message.location.longitude)
        coordinates_stations_correct_2 = (coordinates_stations_2[0], coordinates_stations_2[1])
        distance2 = haversine(user_location_correct, coordinates_stations_correct_2, unit = 'm')
        if int(distance2) < 250:
            quantity += 1
    bot.send_message(message.from_user.id, f'Всего найдено остановок на расстоянии 250м от Вас: {quantity}.')
@bot.message_handler(content_types = ['text'])
def stations_command_message(message):
    global new_arrived_time, verification_time, get_previous_text
    if message.text == 'Узнать расписание для маршрута №1':
        current_time_moscow = datetime.datetime.now(datetime.timezone.utc) + delta
        nowtime = current_time_moscow.strftime("%X")
        if nowtime > '22:00:00' or nowtime < '04:45:00':
            return bot.send_message(message.from_user.id, "Увы, но следующий рейс будет только в 5:30 утра. Просьба подождать!")
        times = nowtime[:5].rsplit(':')
        times = datetime.timedelta(minutes = int(times[1]))
        data_loads = json.load(open('./расписание.json'))
        data = json.dumps(data_loads)
        json_data = json.loads(data)
        route1_daycare = json_data["Маршрут №1"]
        length = 43
        for arrived_time in route1_daycare:
            current_send = 1
            if arrived_time > nowtime: #Знак < - ушедшие рейсы, > - наоборот
                keys = route1_daycare.get(arrived_time)
                length = length - int(keys) + 1
                length = str(length)
                data_loads_previous = json.load(open('./предыдущие_маршруты.json'))
                data_previous = json.dumps(data_loads_previous)
                json_data_previous = json.loads(data_previous)
                route1_previous = json_data_previous["Маршрут №1"]
                get_previous_routers = route1_previous.get(length)[:5]
                if get_previous_routers == '22:00:00':
                    get_previous_text = f'Предыдущий и последний на эти сутки рейс был в `{get_previous_routers}`'
                else:
                    get_previous_text = f'Предыдущий рейс был в `{get_previous_routers}`'
                time_departed = arrived_time[:5].rsplit(':')
                current_time_departed = datetime.timedelta(minutes = int(time_departed[1]))
                nowtime = current_time_departed - times
                nowtime = str(nowtime).rsplit(':')[1]
                verification_time = str(nowtime).rsplit("0")
                if verification_time[0] == "":
                    verification_time = verification_time[1]
                else:
                    verification_time = nowtime
                new_arrived_time = str(arrived_time)[:5]
                keyboard = types.InlineKeyboardMarkup()
                callback_button = types.InlineKeyboardButton(text = "Показать остановки", callback_data = call_data[0]) #stations_1
                keyboard.add(callback_button)
                bot.send_message(message.from_user.id, f'*График движения для маршрута №1* \n\nСледующий автобус отправится с конечной *(ост. «Кладбище» / д/с «Сказка»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
                if current_send == 1:
                    break
    elif message.text == 'Узнать расписание для маршрута №2':
        current_time_moscow = datetime.datetime.now(datetime.timezone.utc) + delta
        nowtime = current_time_moscow.strftime("%X")
        if nowtime > '22:00:00' or nowtime < '04:45:00':
            return bot.send_message(message.from_user.id, "Увы, но следующий рейс будет только в 5:30 утра. Просьба подождать!")
        times = nowtime[:5].rsplit(':')
        times = datetime.timedelta(minutes = int(times[1]))
        data_loads = json.load(open('./расписание.json'))
        data = json.dumps(data_loads)
        json_data = json.loads(data)
        route1_daycare = json_data["Маршрут №2"]
        length = 43
        for arrived_time in route1_daycare:
            current_send = 1
            if arrived_time > nowtime: #Знак < - ушедшие рейсы, > - наоборот
                keys = route1_daycare.get(arrived_time)
                length = length - int(keys) + 1
                length = str(length)
                data_loads_previous = json.load(open('./предыдущие_маршруты.json'))
                data_previous = json.dumps(data_loads_previous)
                json_data_previous = json.loads(data_previous)
                route1_previous = json_data_previous["Маршрут №1"]
                get_previous_routers = route1_previous.get(length)[:5]
                if get_previous_routers == '22:00:00':
                    get_previous_text = f'Предыдущий и последний на эти сутки рейс был в `{get_previous_routers}`'
                else:
                    get_previous_text = f'Предыдущий рейс был в `{get_previous_routers}`'
                time_departed = arrived_time[:5].rsplit(':')
                current_time_departed = datetime.timedelta(minutes = int(time_departed[1]))
                nowtime = current_time_departed - times
                nowtime = str(nowtime).rsplit(':')[1]
                verification_time = str(nowtime).rsplit("0")
                if verification_time[0] == "":
                    verification_time = verification_time[1]
                else:
                    verification_time = nowtime
                new_arrived_time = str(arrived_time)[:5]
                keyboard = types.InlineKeyboardMarkup()
                callback_button = types.InlineKeyboardButton(text = "Показать остановки", callback_data = call_data[1])
                keyboard.add(callback_button)
                bot.send_message(message.from_user.id, f'*График движения для маршрута №2* \n\nСледующий автобус отправится с конечной *(ул. Ивановская (Шоссейная) / ост. «Магазин №5»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
                if current_send == 1:
                    break 
    elif message.text == "⬅️ В главное меню" :
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        owm = OWM('0d16f6ffb7d46c30c1202a765e2cb0fc', config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place('Тейково')
        w = observation.weather
        temp = w.temperature('celsius')['temp']
        temperature = str(temp).rsplit(".")[0]
        if temperature == "-0":
            temperature = "0"
        t = datetime.datetime.now(datetime.timezone.utc) + delta
        nowtime = t.strftime("%d.%m.%Y, %X")
        nowtime_night = t.strftime("%X")
        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        route1_button = types.KeyboardButton(text = "Узнать расписание для маршрута №1")
        route2_button = types.KeyboardButton(text = "Узнать расписание для маршрута №2")
        callback_button = types.KeyboardButton(text = "⬅️ В главное меню")
        stations_button = types.KeyboardButton(text = "Ближайшие остановки")
        donations_button = types.KeyboardButton(text = "Поддержать проект")
        if nowtime_night > '22:00:00' or nowtime_night < '04:45:00':
            keyboard.add(stations_button, donations_button, callback_button)
            bot.send_message(message.chat.id, f"*Главное меню* \n\nНа дворе: `{nowtime}`. \nВ Тейково *{temperature}°*. \n\nК сожалению, ночных рейсов пока что нет. Просьба подождать до первого рейса (`5:30` утра). \nСпасибо за понимание!", parse_mode = 'Markdown', reply_markup = keyboard)
        else:
            keyboard.add(route1_button, route2_button, stations_button, donations_button, callback_button)
            bot.send_message(message.chat.id, f"*Главное меню* \n\nНа дворе: `{nowtime}`. \nВ Тейково *{temperature}°*. \n\nВоспользуйся клавиатурой ниже, чтобы использовать функции бота!", parse_mode = 'Markdown', reply_markup = keyboard)              
    elif message.text == "Поддержать проект":
        keyboard = types.InlineKeyboardMarkup(row_width = 1)
        url_button_qiwi = types.InlineKeyboardButton(text = "Поддержать: QIWI Кошелёк", url = "qiwi.com/n/OVERFLOW16")
        url_button_yandex = types.InlineKeyboardButton(text = "Поддержать: Яндекс.Деньги", url = "money.yandex.ru/to/410015133921329")
        keyboard.add(url_button_qiwi, url_button_yandex)
        bot.send_message(message.chat.id, "Я надеюсь, что этот бот тебе полезен, и очень буду признателен за поддержку нашего проекта! 😊", reply_markup = keyboard)
    elif message.text == "Ближайшие остановки":
        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        button_geo = types.KeyboardButton(text = "Отправить местоположение", request_location = True)
        callback_button = types.KeyboardButton(text = "⬅️ В главное меню")
        keyboard.add(button_geo, callback_button)
        bot.send_message(message.chat.id, "Отправь мне своё местоположение, чтобы узнать список остановок поблизости.", reply_markup = keyboard) 
    else:
        bot.send_message(message.from_user.id, "Хм. Что-то я не припомню такой команды... 🤷🏽‍♂️ \nВоспользуйся /help")
        print(message.from_user.username)
@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == call_data[2]:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "Показать остановки", callback_data = call_data[0])
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'*График движения для маршрута №1* \n\nСледующий автобус отправится с конечной *(ост. «Кладбище» / д/с «Сказка»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
        elif call.data == call_data[3]:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "Показать остановки", callback_data = call_data[1])
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'*График движения для маршрута №2* \n\nСледующий автобус отправится с конечной *(ул. Ивановская (Шоссейная) / ост. «Магазин №5»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
        elif call.data == call_data[0]:
            data_loads = json.load(open('./остановки.json'))
            data = json.dumps(data_loads)
            json_data = json.loads(data)
            route1_daycare = json_data["Маршрут №1"]
            layout = ''
            key = 0
            for station_1 in route1_daycare:
                station_1_true = route1_daycare.get(str(key))
                key += 1
                layout += f'{station_1_true}\n'
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "⬅️ Назад", callback_data = call_data[2])
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'🏢 *Из мкр. Красные Сосенки:* \n{layout}', parse_mode = 'Markdown', reply_markup = keyboard)
        elif call.data == call_data[1]:
            data_loads2 = json.load(open('./остановки.json'))
            data2 = json.dumps(data_loads2)
            json_data2 = json.loads(data2)
            route2_daycare = json_data2["Маршрут №2"]
            layout2 = ''
            key = 0
            for station_2 in route2_daycare:
                station_2_true = route2_daycare.get(str(key))
                key += 1
                layout2 += f'{station_2_true}\n'
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "⬅️ Назад", callback_data = call_data[3])
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'🏢 *Из мкр. Красные Сосенки:* \n{layout2}', parse_mode = 'Markdown', reply_markup = keyboard)
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(f'Возникла ошибка: {e}')
