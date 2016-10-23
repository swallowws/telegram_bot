#!/usr/env/bin python

import sys
from telegram.ext import Updater, CommandHandler
import mysql.connector

try:
    sys.path.append('.private')
    from config import TOKEN, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE
except ImportError as e:
    print("need TOKEN, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE from .private/config.py! \n", e)
    sys.exit(1)

# up = Updater(token=TOKEN)
# dispatcher = up.dispatcher


def start(bot, update):
    msg = "Hello {user_name}! I'm {bot_name}."

    bot.send_message(chat_id=update.message.chat_id,
                     text=msg.format(
                          user_name=update.message.from_user.first_name,
                          bot_name=bot.name))


def get_data_from_database(bot, update):
    connector = mysql.connector.connect(user=MYSQL_USER, database=MYSQL_DATABASE, password=MYSQL_PASSWORD)
    cursor = connector.cursor()
    try:
        query = ("SHOW TABLES;")
        cursor.execute(query)
    except Exception as e:
        print(e)
    finally:
        cursor.close()
        connector.close()

print(get_data_from_database(1,2))