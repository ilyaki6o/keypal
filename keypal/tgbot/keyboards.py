"""All keyboards."""
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

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


update_exist_password = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="YES", callback_data="update_exist_password_yes"),
     InlineKeyboardButton(text="NO", callback_data="update_exist_password_no")]
])


async def buttons_list(buttons: list[str], column: int, type_bt: str):
    """
    Generate a keyboard with multiple pages of buttons.

    Function take 5 string starting with cloumn * 5 from buttons and make keyboard.

    :param buttons: name of buttons
    :param column: current page of buttons
    :param type_bt: type of button (url, login)
    """
    keyboard = InlineKeyboardBuilder()

    set_bt = buttons[column * 5: (column + 1) * 5]

    for el in set_bt:
        keyboard.add(InlineKeyboardButton(text=f"{el}", callback_data=f"{type_bt}_{el}"))

    keyboard.adjust(1)

    if len(buttons) > 5:
        if column == 0:
            keyboard.add(InlineKeyboardButton(text="Next", callback_data=f"next_{type_bt}"))
            keyboard.adjust(1)
        elif (len(buttons) - 1) // 5 == column:
            keyboard.add(InlineKeyboardButton(text="Prev", callback_data=f"prev_{type_bt}"))
            keyboard.adjust(1)
        else:
            keyboard.row(InlineKeyboardButton(text="Prev", callback_data=f"prev_{type_bt}"),
                         InlineKeyboardButton(text="Next", callback_data=f"next_{type_bt}"), width=2)

    return keyboard.as_markup()
