#!/usr/env/bin python
# -*- coding: utf-8 -*-

import sys
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import MySQLdb
import configparser
import datetime


def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    token = config.get('BOT', 'token')
    mysql_user = config.get('MYSQL', 'user')
    mysql_password = config.get('MYSQL', 'password')
    mysql_db = config.get('MYSQL', 'database')
    return token, mysql_user, mysql_password, mysql_db


def start(bot, update):
    msg = "Hello {user_name}! I'm {bot_name}."

    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                          user_name=update.message.from_user.first_name,
                          bot_name=bot.name))


def get_data_from_database():
    db = MySQLdb.connect(host='localhost', user=mysql_user, db=mysql_db, passwd=mysql_password)
    cursor = db.cursor()
    try:
        query = "SELECT " \
                "dateTime, pressure, outTemp, inTemp, outHumidity, windSpeed, windDir, deltarain, geiger, illumination " \
                "FROM " \
                "raw " \
                "ORDER BY " \
                "dateTime " \
                "DESC LIMIT 1;"
        cursor.execute(query)
        data = cursor.fetchall()
        for rec in data:
            dateTime, pressure, outTemp, inTemp, outHumidity, windSpeed, windDir, deltarain, geiger, illumination = rec
        return {'dateTime'     : (int(dateTime) if dateTime is not None else '---'),
                'pressure'     : (int(pressure) if pressure is not None else '---'),
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

    text = """
           Погода на %s: \
           \n\xF0\x9F\x94\xB9 температура воздуха: %s °C \
           \n\xF0\x9F\x94\xB9 давление: %s мм рт.ст \
           \n\xF0\x9F\x94\xB9 освещенность: %s люкс \

           """ % (datetime.datetime.fromtimestamp(int(current_weather['dateTime'])).strftime('%d.%m.%Y, %H:%M'),
                  current_weather['outTemp'],
                  current_weather['pressure'],
                  current_weather['illumination'],
                  )

    bot.send_message(chat_id=update.message.chat_id,
                     text=text)
    print(update.message.chat_id, update.message.text)


def echo(bot, update):
    update.message.reply_text(update.message.text)


def main():

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("tell", tell_weather))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    # dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the you presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    token, mysql_user, mysql_password, mysql_db = read_config('.config/config.cfg')
    main()
