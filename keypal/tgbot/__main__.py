"""Python telegram bot for Bitwarden."""
import telebot
from telebot import types
from ..bitwarden import Bitwarden as bitwd
from pexpect import exceptions as pex_exc

TOKEN = "7342917304:AAG0OneBgGCglwp07pD3TXw5tNPwMCf1E2o"

name = ""
password = ""
bw = None

bot = telebot.TeleBot(TOKEN)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    """
    Realize the installed functionality in response to a inline button press.

    More information in below match-case data structure.

    :param call: object, that contain information about callback.
    """
    data = call.data.strip().lower()

    match data:
        case "registered":
            # log in
            bot.register_next_step_handler(call.message, email_request)
        case "unregistered":
            # registration
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Create account",
                                                  url="https://vault.bitwarden.com/#/register?layout=default"))
            bot.send_message(call.message.chat.id, "Let's set you up with a Bitwarden account."
                             + "To register an account on the Bitwarden website click on the button below.",
                             reply_markup=markup)

            markup_new = types.InlineKeyboardMarkup()
            markup_new.add(types.InlineKeyboardButton("Log in", callback_data="registered"))
            bot.send_message(call.message.chat.id, "Click the button below when you register your account to log in.",
                             reply_markup=markup_new)
        case "get":
            # get password by key
            bot.send_message(call.message.chat.id, "Enter key of password")
            bot.register_next_step_handler(call.message, get_password)
        case "get_all":
            # get all password keys
            data = bw.get_list_of_names()
            res = "List of password keys:\n"

            for el in data:
                res += el + '\n'

            bot.send_message(call.message.chat.id, res)
        case "log_out":
            # log out from bitwarden account
            bw.delete()
            init(call.message)


@bot.message_handler(commands=['start'])
def init(message):
    """
    /start command handling.

    Checks that the user has a bitwarden account.

    :param message: contain information about last message
    """
    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_yes = types.InlineKeyboardButton("Yes", callback_data="registered")
    btn_no = types.InlineKeyboardButton("No", callback_data="unregistered")

    markup.add(btn_yes, btn_no)

    bot.send_message(message.chat.id, "Hello, its KeyPal - telegram bot wrapper for Bitwarden password manager.")
    bot.send_message(message.chat.id, "Do you already have a Bitwarden account?", reply_markup=markup)


# authorization
def email_request(message):
    """
    Request the user's email address.

    :param message: contain information about last message
    """
    bot.send_message(message.chat.id, "Please enter your email")
    bot.register_next_step_handler(message, password_request)


def password_request(message):
    """
    Request the user's password.

    :param message: contain information about last message
    """
    global name
    name = message.text.strip()
    bot.send_message(message.chat.id, "Please enter your password")
    bot.register_next_step_handler(message, authorization_check)


def authorization_check(message):
    """
    Check if the received email and password are correct.

    :param message: contain information about last message
    """
    global password
    global bw

    password = message.text.strip()

    try:
        bw = bitwd.BITWARDEN(name, password)
    except pex_exc.EOF:
        bot.send_message(message.chat.id, "Login or password is wrong. Please try log in again.")
        bot.register_next_step_handler(message, email_request)
    else:
        global_menu(message)


# bitwaren cli requests
def get_password(message):
    """
    Obtain password by key.

    :param message: contain information about last message
    """
    key = message.text.strip()

    data = bw.get_information(key)

    bot.reply_to(message, "Username: {}\n".format(data[0]) + "Password: {}".format(data[1]))


def global_menu(message):
    """
    Send welcome message with main menu.

    :param message: contain information about last message
    """
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
