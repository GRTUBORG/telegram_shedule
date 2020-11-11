import telebot
import datetime
import json
import os
import time

from telebot import types
from haversine import haversine, Unit


token = os.environ.get('bot_token')
bot = telebot.TeleBot(str(token))
print('Бот работает!')
delta = datetime.timedelta(hours = 3, minutes = 0)

@bot.message_handler(commands = ['start'])
def send_welcome(message):
    t = datetime.datetime.now(datetime.timezone.utc) + delta
    nowtime = t.strftime("%X")
    bot.reply_to(message, f'Привет! Текущее время: {nowtime}. Чтобы узнать расписание — пропиши команду (или нажми на неё) /schedule')
@bot.message_handler(commands = ['help'])
def send_help(message):
    bot.reply_to(message, "Привет! Рад, что ты заглянул(а) сюда :) \nПросто используй команду \n/schedule! \nТакже будем очень благодарны за поддержку проекта: /donations.")
@bot.message_handler(commands = ['schedule'])
def switch(message):
    t = datetime.datetime.now(datetime.timezone.utc) + delta
    nowtime = t.strftime("%x %X")
    nowtime_night = t.strftime("%X")
    if nowtime_night > '22:00:00' or nowtime_night < '04:45:00':
        bot.send_message(message.chat.id, f"Текущие дата и время: `{nowtime}`. К сожалению, ночных рейсов пока что нет. Просьба подождать до первого рейса (`5:30` утра). \nСпасибо за понимание!", parse_mode = 'Markdown')
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
        route1_button = types.KeyboardButton(text = "Узнать расписание для маршрута №1")
        route2_button = types.KeyboardButton(text = "Узнать расписание для маршрута №2")
        keyboard.add(route1_button, route2_button)
        bot.send_message(message.chat.id, f"Текущие дата и время: `{nowtime}`. Воспользуйся клавиатурой ниже, чтобы узнать расписание!", parse_mode = 'Markdown', reply_markup = keyboard)
@bot.message_handler(commands = ['donations'])
def donations(message):
    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    url_button_bank = types.InlineKeyboardButton(text = "Поддержать: Перевод с карты на карту", url = "https://securepayments.sberbank.ru/payment/merchants/p2p_transfer/index.html?_ga=2.34322209.1897604948.1605089593-1741886018.1604938142")
    url_button_qiwi = types.InlineKeyboardButton(text = "Поддержать: QIWI Кошелёк", url = "qiwi.com/n/OVERFLOW16")
    url_button_yandex = types.InlineKeyboardButton(text = "Поддержать: Яндекс.Деньги", url = "money.yandex.ru/to/410015133921329")
    keyboard.add(url_button_bank, url_button_qiwi, url_button_yandex)
    bot.send_message(message.chat.id, "Я надеюсь, что этот бот тебе полезен, и очень буду признателен за поддержку нашего проекта!", reply_markup = keyboard)
@bot.message_handler(commands = ["info"])
def geophone(message):
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    button_geo = types.KeyboardButton(text = "Отправить местоположение", request_location = True)
    keyboard.add(button_geo)
    bot.send_message(message.chat.id, "Отправь мне своё местоположение, чтобы узнать список остановок поблизости.", reply_markup=keyboard)  
@bot.message_handler(content_types = ['location'])
def handle_loc(message):
    user_location = [message.location.latitude, message.location.longitude]
    user_location_lat = user_location[0]
    user_location_lon = user_location[1]
    data_loads_previous = json.load(open('./координаты_остановок.json'))
    data_previous = json.dumps(data_loads_previous)
    json_data_previous = json.loads(data_previous)
    route1_previous = json_data_previous["Маршрут №1"]
    key = 0
    while key < 23:
        key = str(key)
        coordinates_stations = route1_previous.get(key)
        key = int(key)
        key += 1
    user_location_correct = (user_location_lat, user_location_lon)
    coordinates_stations_correct = (coordinates_stations[0], coordinates_stations[1])
    distance = haversine(user_location_correct, coordinates_stations_correct, unit = 'm')
    print(distance)
    if int(distance) > 150:
        bot.send_message(message.chat.id, "Остановок в радиусе 150 м. от тебя, к сожалению, нет.")
    else:
        data_loads = json.load(open('./остановки.json'))
        data = json.dumps(data_loads)
        json_data = json.loads(data)
        route1_daycare = json_data["Маршрут №1"]
        key = str(key)
        route1_daycare_print = route1_daycare.get(key)
        key = int(key)
        bot.send_message(message.chat.id, f"Все остановки в радиусе 150 м. от тебя: {route1_daycare_print}")

call_data = ["stations_1", "stations_2", "back_stations1", "back_stations2"]
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
                bot.send_message(message.from_user.id, f'Следующий автобус отправится с конечной *(ост. «Кладбище» / д/с «Сказка»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
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
                bot.send_message(message.from_user.id, f'Следующий автобус отправится с конечной *(ул. Ивановская (Шоссейная) / ост. «Магазин №5»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
                if current_send == 1:
                    break
                
    else:
        bot.send_message(message.from_user.id, "Хм. Что-то я не припомню такой команды... Воспользуйся /help")
        print(message.from_user.username)
	
@bot.callback_query_handler(func = lambda call: True)
def callback_inline(call):
    if call.message:
        if call.data == call_data[2]:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "Показать остановки", callback_data = "stations_1")
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'Следующий автобус отправится с конечной *(ост. «Кладбище» / д/с «Сказка»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
        elif call.data == call_data[3]:
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "Показать остановки", callback_data = "stations_2")
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'Следующий автобус отправится с конечной *(ост. «Кладбище» / д/с «Сказка»)* станции в `{new_arrived_time}`. До его отправления осталось `{verification_time}` мин. \n{get_previous_text}', parse_mode = 'Markdown', reply_markup = keyboard)
        elif call.data == "stations_1":
            data_loads = json.load(open('./остановки.json'))
            data = json.dumps(data_loads)
            json_data = json.loads(data)
            route1_daycare = json_data["Маршрут №1"]
            layout = ''
            for station_1 in route1_daycare:
                station_1_true = station_1.replace('  ', '\n')
                layout += station_1_true
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "« Назад", callback_data = call_data[2])
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'*Из мкр. Красные Сосенки:* \n{layout}', parse_mode = 'Markdown', reply_markup = keyboard)
        elif call.data == "stations_2":
            data_loads2 = json.load(open('./остановки.json'))
            data2 = json.dumps(data_loads2)
            json_data2 = json.loads(data2)
            route2_daycare = json_data2["Маршрут №2"]
            layout2 = ''
            for station_2 in route2_daycare:
                station_2_true = station_2.replace('  ', '\n')
                layout2 += station_2_true
            keyboard = types.InlineKeyboardMarkup()
            callback_button = types.InlineKeyboardButton(text = "« Назад", callback_data = call_data[3])
            keyboard.add(callback_button)
            bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = f'*Из мкр. Красные Сосенки:* \n{layout2}', parse_mode = 'Markdown', reply_markup = keyboard)
    
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(3)
            print(f'Возникла ошибка: {e}')
