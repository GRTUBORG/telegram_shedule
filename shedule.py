import telebot
import time
import datetime
import json
import os

from telebot import types

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
	bot.reply_to(message, "Привет! Рад, что ты заглянул сюда :) \nПросто используй команду /schedule!")

@bot.message_handler(commands = ['schedule'])
def switch(message):
    t = datetime.datetime.now(datetime.timezone.utc) + delta
    nowtime = t.strftime("%x %X")
    keyboard = types.ReplyKeyboardMarkup(row_width = 1, resize_keyboard = True)
    route1_button = types.KeyboardButton(text = "Узнать расписание для маршрута №1")
    route2_button = types.KeyboardButton(text = "Узнать расписание для маршрута №2")
    keyboard.add(route1_button, route2_button)
    bot.send_message(message.chat.id, f"Текущие дата и время: {nowtime}. Воспользуйся клавиатурой ниже, чтобы узнать расписание!", reply_markup = keyboard)


@bot.message_handler(content_types = ['text'])
def weather_command_message(message):
    if message.text == 'Узнать расписание для маршрута №1':
        current_time_moscow = datetime.datetime.now(datetime.timezone.utc) + delta
        nowtime = current_time_moscow.strftime("%X")
        times = nowtime[:5].rsplit(':')
        times = datetime.timedelta(minutes = int(times[1]))
        data_loads = json.load(open('./расписание.json'))
        data = json.dumps(data_loads)
        json_data = json.loads(data)
        route1_daycare = json_data["Маршрут №1"]
        for arrived_time in route1_daycare:
            current_send = 1
            if arrived_time > nowtime: #Знак < - ушедшие рейсы, > - наоборот
                time_departed = arrived_time[:5].rsplit(':')
                current_time_departed = datetime.timedelta(minutes = int(time_departed[1]))
                nowtime = current_time_departed - times
                nowtime = str(nowtime).rsplit(':')[1]
                verification_time = str(nowtime).rsplit("0")
                if verification_time[0] == "":
                    verification_time = verification_time[1]
                else:
                    verification_time = nowtime
                bot.send_message(message.from_user.id, f'Следующий автобус отправится с конечной станции в {str(arrived_time)[:5]}. До его отправления осталось {verification_time} мин.') 
                if current_send == 1:
                    break
    elif message.text == 'Узнать расписание для маршрута №2':
        current_time_moscow = datetime.datetime.now(datetime.timezone.utc) + delta
        nowtime = current_time_moscow.strftime("%X")
        times = nowtime[:5].rsplit(':')
        times = datetime.timedelta(minutes = int(times[1]))
        data_loads = json.load(open('./расписание.json'))
        data = json.dumps(data_loads)
        json_data = json.loads(data)
        route1_daycare = json_data["Маршрут №2"]
        for arrived_time in route1_daycare:
            current_send = 1
            if arrived_time > nowtime: #Знак < - ушедшие рейсы, > - наоборот
                time_departed = arrived_time[:5].rsplit(':')
                current_time_departed = datetime.timedelta(minutes = int(time_departed[1]))
                nowtime = current_time_departed - times
                nowtime = str(nowtime).rsplit(':')[1]
                verification_time = str(nowtime).rsplit("0")
                if verification_time[0] == "":
                    verification_time = verification_time[1]
                else:
                    verification_time = nowtime
                bot.send_message(message.from_user.id, f'Следующий автобус отправится с конечной станции в {str(arrived_time)[:5]}. До его отправления осталось {verification_time} мин.') 
                if current_send == 1:
                    break
    else:
        bot.send_message(message.from_user.id, "Хм. Что-то я не припомню такой команды... Воспользуйся /help")
        print(message.from_user.username)

	
bot.polling(none_stop = True)
