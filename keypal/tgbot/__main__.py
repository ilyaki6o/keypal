import telebot
from telebot import types
from ..bitwarden import Bitwarden as bitwd

TOKEN = "7342917304:AAG0OneBgGCglwp07pD3TXw5tNPwMCf1E2o"

name = ""
password = ""
bw = None

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def init(message):
    bot.send_message(message.chat.id, "Hello, its Bitwarden telegram bot wrapper! Please, sing in.")
    bot.send_message(message.chat.id, "Write your login")
    bot.register_next_step_handler(message, user_name)

def user_name(message):
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Write your password")
    bot.register_next_step_handler(message, user_pass)


def user_pass(message):
    global password
    password = message.text.strip()

    bot.send_message(message.chat.id, f"User {name} registered")

    global_menu(message)


def global_menu(message):
    
    markup = types.InlineKeyboardMarkup()

    button_get = types.InlineKeyboardButton("Get password", callback_data="get")
    button_get_all = types.InlineKeyboardButton("Get all passwords", callback_data="get_all")
    button_set = types.InlineKeyboardButton("Set password", callback_data="set")
    button_log_out = types.InlineKeyboardButton("Sing out", callback_data="log_out")

    markup.row(button_get, button_set)
    markup.row(button_get_all)
    markup.row(button_log_out)

    markup_keyboard = types.ReplyKeyboardMarkup()

    keyboard_get_all = types.KeyboardButton("Get all passwords")
    keyboard_log_out = types.KeyboardButton("Sing out")

    markup_keyboard.add(keyboard_get_all)
    markup_keyboard.add(keyboard_log_out)

    bot.send_message(message.chat.id, 'Welcome', reply_markup=markup_keyboard)
    bot.send_message(message.chat.id, "KeyPal - your Bitwarden password client", reply_markup=markup)

bot.infinity_polling()
