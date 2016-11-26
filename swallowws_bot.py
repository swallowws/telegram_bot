#!/usr/env/bin python
# -*- coding: utf-8 -*-

import sys
from telegram import ChatAction, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import MySQLdb
import configparser
import datetime
import os


CONFIG_WAY = "local"

if CONFIG_WAY == "local":
    config = configparser.ConfigParser()
    config.read('.config/config.cfg')
    token = config.get('BOT', 'token')
    mysql_user = config.get('MYSQL', 'user')
    mysql_passwd = config.get('MYSQL', 'password')
    mysql_db = config.get('MYSQL', 'database')
    config = {'token': token, 'mysql_user': mysql_user, 'mysql_passwd': mysql_passwd, 'mysql_db': mysql_db}
elif CONFIG_WAY == "heroku":
    token = os.environ['TOKEN']
    mysql_user = os.environ['MYSQL_USER']
    mysql_passwd = os.environ['MYSQL_PASSWD']
    mysql_db = os.environ['MYSQL_DB']
    config = {'token': token, 'mysql_user': mysql_user, 'mysql_passwd': mysql_passwd, 'mysql_db': mysql_db}
else:
    print('nor \"local\" or \"heroku\" in CONFIG')
    raise Exception


def start(bot, update):
    custom_keyboard = [["/tell"]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    msg = "Привет! \xE2\x9C\x8C" \
          "\nЧтобы узнать погоду, нажми на кнопку\xF0\x9F\x91\x87 или отправь мне /tell"
    bot.send_message(chat_id=update.message.chat_id,
                     text=msg, reply_markup=reply_markup)


def get_data_from_database():
    db = MySQLdb.connect(host='localhost', user=config['mysql_user'], passwd=config['mysql_passwd'], db=config['mysql_db'])
    cursor = db.cursor()
    try:
        query = "SELECT dateTime, pressure, outTemp, inTemp, outHumidity, windSpeed, windDir, deltarain, geiger, illumination FROM raw ORDER BY dateTime DESC LIMIT 1;"
        cursor.execute(query)
        data = cursor.fetchall()
        for rec in data:
            dateTime, pressure, outTemp, inTemp, outHumidity, windSpeed, windDir, deltarain, geiger, illumination = rec
        return {'dateTime'     : (int(dateTime) if dateTime is not None else '---'),
                'pressure'     : (int(pressure * 0.750064) if pressure is not None else '---'),  # hPa to mmHg
                'outTemp'      : (round(float(outTemp), 1) if outTemp is not None else '---'),
                'inTemp'       : (round(float(inTemp), 1) if inTemp is not None else '---'),
                'outHumidity'  : (int(outHumidity) if outHumidity is not None else '---'),
                'windSpeed'    : (round(float(windSpeed), 1) if windSpeed is not None else '---'),
                'deltarain'    : (int(deltarain) if deltarain is not None else '---'),
                'geiger'       : (int(geiger) if geiger is not None else '---'),
                'illumination' : (int(illumination) if illumination is not None else '---')
                }
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()


def tell_weather(bot, update):
    current_weather = get_data_from_database()
    msg = """
           Погодные данные на %s: \
           \n\xE2\x99\xA8 Температура воздуха: *%s* °C \
           \n\xF0\x9F\x92\xAA Давление: *%s* мм рт.ст \
           \n\xF0\x9F\x92\xA6 Влажность: *%s* %% \
           \n\xF0\x9F\x92\xA8 Ветер: *%s* м/с\
           \n\xE2\x98\x94 Дождь: *%s* мм/ч\
           \n\xF0\x9F\x92\xA1 Освещенность: *%s* люкс \
           \n\xF0\x9F\x92\x9A[Ласточка](http://weather.thirdpin.ru)\xF0\x9F\x92\x9A \
           """ % (datetime.datetime.fromtimestamp(int(current_weather['dateTime'])).strftime('%d.%m.%Y, %H:%M'),
                  current_weather['outTemp'],
                  current_weather['pressure'],
                  current_weather['outHumidity'],
                  current_weather['windSpeed'],
                  current_weather['deltarain'],
                  current_weather['illumination']
                  )

    bot.send_message(chat_id=update.message.chat_id, text=msg,parse_mode=ParseMode.MARKDOWN)
    print(update.message.chat_id, update.message.text)


def send_kitty(bot, update):
    random_kitty = "http://thecatapi.com/api/images/get?format=src"
    bot.sendChatAction(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    bot.sendPhoto(chat_id=update.message.chat_id, photo=random_kitty)


def main():

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config['token'])

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("tell", tell_weather))
    dp.add_handler(CommandHandler("kitty", send_kitty))

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
