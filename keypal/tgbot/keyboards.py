"""All keyboards."""
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

import gettext
from pathlib import Path

_path = str(Path(__file__).parents[1])

LOCALES = {
    "ru_RU.UTF-8": gettext.translation("tgbot", _path, fallback=True),
    "en_US.UTF-8": gettext.NullTranslations(),
}

locale = LOCALES["en_US.UTF-8"]


def _(local, text):
    """Redefine for choose locale."""
    return local.gettext(text)


start = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=_(locale, "Yes"), callback_data="log_in"),
     InlineKeyboardButton(text=_(locale, "No"), callback_data="registration")]
])

reg_account = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=_(locale, "Create account"), url="https://vault.bitwarden.com/#/register?layout=default")]
])

log_in = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=_(locale, "Log in"), callback_data="log_in")]
])

new_session = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=_(locale, "Start Session"), callback_data="start_session")],
])

main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=_(locale, "GET"), callback_data="get_password")],
    [InlineKeyboardButton(text=_(locale, "SET"), callback_data="set_password"),
     InlineKeyboardButton(text=_(locale, "UPDATE"), callback_data="update_password")],
])


update_exist_password = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text=_(locale, "Yes"), callback_data="update_exist_password_yes"),
     InlineKeyboardButton(text=_(locale, "No"), callback_data="update_exist_password_no")]
])


translate = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="RU", callback_data="translate_ru"),
     InlineKeyboardButton(text="EN", callback_data="translate_en")]
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
            keyboard.add(InlineKeyboardButton(text=_(locale, "Next"), callback_data=f"next_{type_bt}"))
            keyboard.adjust(1)
        elif (len(buttons) - 1) // 5 == column:
            keyboard.add(InlineKeyboardButton(text=_(locale, "Prev"), callback_data=f"prev_{type_bt}"))
            keyboard.adjust(1)
        else:
            keyboard.row(InlineKeyboardButton(text=_(locale, "Prev"), callback_data=f"prev_{type_bt}"),
                         InlineKeyboardButton(text=_(locale, "Next"), callback_data=f"next_{type_bt}"), width=2)

    return keyboard.as_markup()
