#!/usr/env/bin python

import sys
from telegram.ext import Updater, CommandHandler
import MySQLdb
import configparser

# try:
#    sys.path.append('.private')
#    from config import TOKEN, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
# except ImportError as e:
#    print("need TOKEN, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE from .private/config.py! \n", e)
#    sys.exit(1)

# up = Updater(token=TOKEN)
# dispatcher = up.dispatcher


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
        return {'dateTime'     : (int(dateTime) if dateTime is not None else None),
                'pressure'     : (int(pressure) if pressure is not None else None),
                'outTemp'      : (float(outTemp) if outTemp is not None else None),
                'inTemp'       : (float(inTemp) if inTemp is not None else None),
                'outHumidity'  : (int(outHumidity) if outHumidity is not None else None),
                'windSpeed'    : (float(windSpeed) if windSpeed is not None else None),
                'deltarain'    : (int(deltarain) if deltarain is not None else None),
                'geiger'       : (int(geiger) if geiger is not None else None),
                'illumination' : (int(illumination) if illumination is not None else None)}
    except Exception as e:
        print(e)
        return None
    finally:
        cursor.close()
        db.close()


token, mysql_user, mysql_password, mysql_db = read_config('.config/config.cfg')
data = get_data_from_database()
print(data)