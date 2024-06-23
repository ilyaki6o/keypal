from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes", callback_data="log_in"), 
     InlineKeyboardButton(text="No", callback_data="registration")]
])

reg_account = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Create account", url="https://vault.bitwarden.com/#/register?layout=default")]
])

log_in = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Log in", callback_data="log_in")]
])

new_session = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Start Session", callback_data="start_session")],
])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="GET", callback_data="get_password")],
    [InlineKeyboardButton(text="SET", callback_data="set_password"),
     InlineKeyboardButton(text="UPDATE", callback_data="update_password")],
])
