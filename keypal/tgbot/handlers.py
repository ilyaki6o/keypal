"""All logic of telegram bot."""
# from ..bitwarden import Bitwarden as bitwd
# from pexpect import exceptions as pex_exc
from urllib.parse import urlparse
import validators

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

import gettext
from pathlib import Path

_path = str(Path(__file__).parents[1])

LOCALES = {
    "ru_RU.UTF-8": gettext.translation("tgbot", _path, fallback=True),
    "en_US.UTF-8": gettext.NullTranslations(),
}


def _(local, text):
    """Redefine for choose locale."""
    return local.gettext(text)


from . import keyboards as kb
from ..database import database as db
from ..bitwarden import bitwarden as bw

router = Router()

clients = {}


class Client():
    url_column = 0
    login_column = 0
    chosen_urls = []
    chosen_logins = []
    auth_db = None
    bw_client = None
    locale = LOCALES["en_US.UTF-8"]

    def set_db(self, db):
        self.auth_db = db
    
    def get_db(self):
        return self.auth_db
    
    def set_bw(self, bw):
        self.bw_client = bw

    def get_bw(self):
        return self.bw_client

class User(StatesGroup):
    """State sequence for user authorization."""

    client_id = State()
    client_secret = State()


class MasterP(StatesGroup):
    """State for start session."""

    master_password = State()


class Password_flow(StatesGroup):
    """State sequence for get and update password."""

    url = State()
    login = State()
    password = State()
    work_type = State()


class Set_Password(StatesGroup):
    """State sequence for set password."""

    url = State()
    login = State()
    password = State()


################# Commands


@router.message(CommandStart())
async def start(message: Message):
    """/start command handler."""
    clients[message.chat.id] = Client()
    auth_db = db.Database(message.chat.id)
    clients[message.chat.id].set_db(auth_db)
    locale = clients[message.chat.id].locale

    # await message.answer(str(message.chat.id))


    if (data := auth_db.check()):
        bw_client = bw.BitwardenClient(client_dir=str(message.chat.id),
                                       client_id=data[0],
                                       client_secret=data[1])

        clients[message.chat.id].set_bw(bw_client)

        match bw_client.get_status():
            case "unauthenticated":
                try:
                    bw_client.login(client_id=data[0],
                                    client_secret=data[1])
                except Exception:
                    print("Incorrect data in db")
                    exit(1)

                await start_session(message)
            case "locked":
                await start_session(message)
            case "unlocked":
                await main_menu(message)
    else:
        await message.answer(_(locale, "Hello, its KeyPal - telegram bot wrapper for Bitwarden password manager."))
        await message.answer(_(locale, "Do you already have a Bitwarden account?"), reply_markup=kb.start)


@router.message(F.text, Command("translate"))
async def translate(message: Message):
    locale = clients[message.chat.id].locale
    await message.answer(_(locale, "Please choose locale"), reply_markup=kb.translate)


@router.message(F.text, Command("close_session"))
async def close_session(message: Message):
    bw_client = clients[message.chat.id].get_bw()
    bw_client.lock()
    await start_session(message)


@router.message(F.text, Command("log_out"))
async def log_out(message: Message):
    bw_client = clients[message.chat.id].get_bw()
    bw_client.logout()
    await start(message)


@router.message(F.text, Command("get_status"))
async def cur_status(message: Message):
    bw_client = clients[message.chat.id].get_bw()
    await message.answer(f"cur status: {bw_client.get_status()}")

################# Callback


@router.callback_query(F.data.startswith("translate_"))
async def choose_locale(call: CallbackQuery):
    language = str(call.data)[-2:]

    match language:
        case "en":
            clients[call.message.chat.id].locale = LOCALES["en_US.UTF-8"]
        case "ru":
            clients[call.message.chat.id].locale= LOCALES["ru_RU.UTF-8"]

    await call.answer("")

    await main_menu(call.message)


@router.callback_query(F.data == "log_in")
async def log_in(call: CallbackQuery, state: FSMContext):
    """
    Log in button handler.

    Start authorization process.
    """
    await request_client_id(call.message, state)
    await call.answer('')


@router.callback_query(F.data == "registration")
async def registration(call: CallbackQuery):
    """
    "No" button hendler when client says he doesn't have a bitwarden account.

    Offers to create an account and log in.
    """
    locale = clients[call.message.chat.id].locale

    await call.message.answer(_(locale, "Let's set you up with a Bitwarden account.\n") +
                              _(locale, "To register an account on the Bitwarden website click on the button below."),
                              reply_markup=kb.reg_account)
    await call.message.answer(_(locale, "Click the button below when you register your account to log in."),
                              reply_markup=kb.log_in)
    await call.answer('')


@router.callback_query(F.data == "start_session")
async def master_password(call: CallbackQuery, state: FSMContext):
    """
    Start session button hendler.

    Check client master password.
    """
    locale = clients[call.message.chat.id].locale
    await state.set_state(MasterP.master_password)
    await call.message.answer(_(locale, "Please enter your master password"))
    await call.answer('')


@router.callback_query(F.data == "get_password")
async def get_password(call: CallbackQuery, state: FSMContext):
    """
    'GET' button on main menu hendler.

    Requests the address of the website where you need to enter your password.
    """
    locale = clients[call.message.chat.id].locale
    await call.message.answer(_(locale, "Enter the url to search for the password"))
    await state.set_state(Password_flow.url)
    await state.update_data(work_type=str(call.data))
    await call.answer('')


@router.callback_query(F.data == "delete_password")
async def delete_password(call: CallbackQuery, state: FSMContext):
    """
    'DETELE' button on main menu hendler.

    Requests the address of the website where you need to delete your password.
    """
    locale = clients[call.message.chat.id].locale
    await call.message.answer(_(locale, "Enter the url to search for the password"))
    await state.set_state(Password_flow.url)
    await state.update_data(work_type=str(call.data))
    await call.answer('')


@router.callback_query(F.data == "set_password")
async def set_password(call: CallbackQuery, state: FSMContext):
    """
    'SET' button in main menu handler.

    Requests the address of the website where you want to create new account.
    """
    locale = clients[call.message.chat.id].locale

    await call.message.answer(_(locale, "Enter the address of the site for which you want to save the password"))
    await state.set_state(Set_Password.url)
    await call.answer("")


@router.callback_query(F.data.startswith("url_"))
async def accept_url(call: CallbackQuery, state: FSMContext):
    """
    Url address selection button handler.

    Catch url button press and save url in memmory.
    """
    correct_url = str(call.data)[4:]

    await state.update_data(url=correct_url)
    await state.set_state(Password_flow.login)
    await choose_login(call.message, state)
    await call.answer("")


@router.callback_query(F.data.startswith("login_"))
async def accept_login(call: CallbackQuery, state: FSMContext):
    """
    Login selection button handler.

    Catch login button press and save login in memmory.
    """
    correct_login = str(call.data)[6:]

    await state.update_data(login=correct_login)
    await check_work_type(call.message, state)
    await call.answer("")


@router.callback_query(F.data.startswith("next_"))
async def next_column(call: CallbackQuery):
    """
    "Next" button hendler.

    Generate next page of buttons (url or login).
    """
    locale = clients[call.message.chat.id].locale
    state = str(call.data)[5:]

    match state:
        case "url":
            clients[call.message.chat.id].url_column += 1
            url_column = client[call.message.chat.id].url_column
            chosen_urls = client[call.message.chat.id].chosen_urls
            await call.message.edit_text(_(locale, "Please select website"),
                                         reply_markup=await kb.buttons_list(chosen_urls, url_column, "url"))
        case "login":
            clients[call.message.chat.id].login_column += 1
            chosen_logins = clients[call.message.chat.id].chosen_logins
            login_column = clients[call.message.chat.id].login_column
            await call.message.edit_text(_(locale, "Please select login"),
                                         reply_markup=await kb.buttons_list(chosen_logins, login_column, "login"))

    await call.answer("")


@router.callback_query(F.data.startswith("prev_"))
async def prev_column(call: CallbackQuery):
    """
    "Prev" button hendler.

    Generate previous page of buttons (url or login).
    """
    locale = clients[call.message.chat.id].locale
    state = str(call.data)[5:]

    match state:
        case "url":
            clients[call.message.chat.id].url_column -= 1
            url_column = client[call.message.chat.id].url_column
            chosen_urls = client[call.message.chat.id].chosen_urls
            await call.message.edit_text(_(locale, "Please select website"),
                                         reply_markup=await kb.buttons_list(chosen_urls, url_column, "url"))
        case "login":
            clients[call.message.chat.id].login_column -= 1
            chosen_logins = clients[call.message.chat.id].chosen_logins
            login_column = clients[call.message.chat.id].login_column
            await call.message.edit_text(_(locale, "Please select login"),
                                         reply_markup=await kb.buttons_list(chosen_logins, login_column, "login"))

    await call.answer("")


# @router.callback_query(F.data.startswith("update_exist_password_"))
# async def chenge_exist_password(call: CallbackQuery, state: FSMContext):
#     """
#     "Yes" and 'No' button hendler for keyboard while set new password.
#
#     With 'Yes' request new password.
#     With 'No' stop set password process and display main menu.
#     """
#     type_bt = str(call.data)[-3:]
#
#     match type_bt:
#         case "yes":
#             await call.message.answer(_(locale, "Please enter new password"))
#             await state.set_state(Set_Password.password)
#         case "_no":
#             await call.message.edit_text(_(locale, "Adding a password is canceled"))
#             await state.clear()
#             await main_menu(call.message)
#
#     await call.answer("")


@router.callback_query(F.data.startswith("delete_password_"))
async def delete_password_callback(call: CallbackQuery, state: FSMContext):
    """
    "Yes" and 'No' button hendler for keyboard while delete password.

    With 'Yes' delete password and display main menu.
    With 'No' stop  process and display main menu.
    """
    locale = clients[call.message.chat.id].locale
    bw_client = clients[call.message.chat.id].get_bw()
    type_bt = str(call.data)[-3:]


    match type_bt:
        case "yes":
            data = await state.get_data()
            bw_data = bw_client.search_items_with_uri_part(data["url"])

            for el in bw_data:
                if data["login"] == el["login"]["username"]:
                    bw_client.del_password_by_id(el["id"])
                    break

            await call.message.edit_text(_(locale, "Password removed"))
        case "_no":
            await call.message.edit_text(_(locale, "Password remove is canseled"))
            
    await state.clear()
    await main_menu(call.message)


####### Func


async def start_session(message: Message):
    """Display 'start session' button."""
    locale = clients[message.chat.id].locale
    await message.answer(_(locale, "Click the button below to start new session"), reply_markup=kb.new_session)


async def request_client_id(message: Message, state: FSMContext):
    """Request client_id."""
    locale = clients[message.chat.id].locale
    await state.set_state(User.client_id)
    await message.answer(_(locale, "Please enter your client_id"))


async def main_menu(message: Message):
    """Display main menu."""
    locale = clients[message.chat.id].locale
    await message.answer(_(locale, "Welcome to KeyPal"), reply_markup=kb.main_menu)


############# States


@router.message(User.client_id)
async def request_client_secret(message: Message, state: FSMContext):
    """Catch message with client_id and request client_secret."""
    locale = clients[message.chat.id].locale
    await state.update_data(client_id=message.text)
    await state.set_state(User.client_secret)
    await message.answer(_(locale, "Please enter your client_secret"))


@router.message(User.client_secret)
async def auth_check(message: Message, state: FSMContext):
    """Catch message with client_secret and make authorization check."""
    locale = clients[message.chat.id].locale
    await state.update_data(client_secret=message.text)
    data = await state.get_data()

    bw_client = bw.BitwardenClient(client_dir=str(message.chat.id),
                                   client_id=data['client_id'],
                                   client_secret=data["client_secret"]) 
    # await message.answer(f"Your client_id: {data['client_id']}\nYour client_secret: {data['client_secret']}")

    clients[message.chat.id].set_bw(bw_client)

    try:
        bw_client.login(client_id=data["client_id"],
                        client_secret=data["client_secret"])
    except Exception:
        await message.answer(_(locale, "Cannot connect to your account. client_id or client_secret is not correct"))
        await state.clear()
        await request_client_id(message, state)
    else:
        auth_db = clients[message.chat.id].get_db()
        auth_db.add_new(client_id=data["client_id"],
                        client_secret=data["client_secret"])

        await state.clear()
        await start_session(message)


@router.message(MasterP.master_password)
async def check_master_password(message: Message, state: FSMContext):
    """Catch message with master password and if its correct."""
    locale = clients[message.chat.id].locale
    await state.update_data(master_password=message.text)
    data = await state.get_data()
    bw_client = clients[message.chat.id].get_bw()

    # await message.answer(f"Your master_password: {data['master_password']}")

    try:
        bw_client.unlock(data['master_password'])
    except Exception:
        await message.answer(_(locale, "Incorrect master password. Try again."))
        await state.clear()
        await state.set_state(MasterP.master_password)
        await message.answer(_(locale, "Please enter your master password"))
    else:
        await state.clear()
        await main_menu(message)


@router.message(Password_flow.url)
async def choose_url(message: Message, state: FSMContext):
    """
    Catch message with url string and hendle it.

    Check if url with this substring exist and displey keyboard with appropriate urls.
    Request to choose url.
    """
    locale = clients[message.chat.id].locale
    bw_client = clients[message.chat.id].get_bw()

    url = message.text
    cur_urls= bw_client.search_items_with_uri_part(url)
    chosen_urls = []
    url_column = 0

    for el in cur_urls:
        for j in el["login"]["uris"]:
            if str(url) in j["uri"]:
                chosen_urls.append(j["uri"])

    chosen_urls = list(set(chosen_urls))
    chosen_urls = sorted(chosen_urls)

    clients[message.chat.id].chosen_urls = chosen_urls
    clients[message.chat.id].url_column = url_column

    # await message.answer(str(chosen_urls))

    if len(chosen_urls) == 0:
        await message.answer(_(locale, "There are no records for this website"))
        await state.clear()
        await main_menu(message)
    elif len(chosen_urls) == 1:
        await message.answer(_(locale, "Selected website {}").format(chosen_urls[0]), disable_web_page_preview=True)
        await state.update_data(url=chosen_urls[0])
        await state.set_state(Password_flow.login)
        await choose_login(message, state)
    else:
        await message.answer(_(locale, "Please select website"),
                             reply_markup=await kb.buttons_list(chosen_urls, url_column, "url"))


async def choose_login(message: Message, state: FSMContext):
    """Displey account logins on selected site and request to choose login."""
    locale = clients[message.chat.id].locale
    bw_client = clients[message.chat.id].get_bw()

    chosen_logins, login_column = [], 0
    data = await state.get_data()

    bw_data = bw_client.search_items_with_uri_part(data["url"])

    for el in bw_data:
        chosen_logins.append(el["login"]["username"])

    chosen_logins = sorted(chosen_logins)
    clients[message.chat.id].chosen_logins = chosen_logins
    clients[message.chat.id].login_column = login_column

    await message.answer(_(locale, "Please select login"),
                         reply_markup=await kb.buttons_list(chosen_logins, login_column, "login"))


async def check_work_type(message: Message, state: FSMContext):
    """Determine whether it's a 'GET' or 'UPDATE' process."""
    bw_client = clients[message.chat.id].get_bw()
    password = ""

    data = await state.get_data()
    bw_data = bw_client.search_items_with_uri_part(data["url"])

    for el in bw_data:
        if el["login"]["username"] == data["login"]:
            password = el["login"]["password"]

    await state.update_data(password=password)
    data = await state.get_data()

    if data["work_type"] == "get_password":
        await send_password(message, state)
    elif data["work_type"] == "delete_password":
        await delete_password_query(message, state)

async def send_password(message: Message, state: FSMContext):
    """Displat login and password for selected website."""
    locale = clients[message.chat.id].locale
    data = await state.get_data()

    res = _(locale, "For website: {}\n\nLogin: <code>{}</code>\nPassword: <code>{}</code>").format(data["url"],
                                                                                        data["login"],
                                                                                        data["password"])

    await message.answer(res, parse_mode=ParseMode.HTML, disable_web_page_preview=True)

    await state.clear()
    await main_menu(message)


async def delete_password_query(message: Message, state: FSMContext):
    """Delete password from bitwaeden."""
    locale = clients[message.chat.id].locale
    data = await state.get_data()

    res = _(locale, "For website: {}\n\nLogin: <code>{}</code>\nPassword: <code>{}</code>").format(data["url"],
                                                                                        data["login"],
                                                                                        data["password"])

    await message.answer(res, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
    await message.answer(_(locale, "Are you sure you want to delete the password"), reply_markup=kb.delete_password)


@router.message(Set_Password.password)
async def set_new_password(message: Message, state: FSMContext):
    """Catch password for new account and save in in memmory."""
    locale = clients[message.chat.id].locale
    bw_client = clients[message.chat.id].get_bw()

    await state.update_data(password=message.text)
    data = await state.get_data()

    bw_client.create_password(uri=data["url"],
                              username=data["login"],
                              password=data["password"])

    await send_password(message, state)


@router.message(Set_Password.url)
async def url_for_set(message: Message, state: FSMContext):
    """Catch url string, save it and request login for new account."""
    locale = clients[message.chat.id].locale
    url = str(message.text)

    if validators.url(url):
        url = urlparse(url).netloc
        # url = '.'.join(url.split('.')[-2:])

    await state.update_data(url=url)

    await message.answer(_(locale, "Enter the login of the account on this website for which you want to save a password"))
    await state.set_state(Set_Password.login)


@router.message(Set_Password.login)
async def login_for_set(message: Message, state: FSMContext):
    """
    Catch login of new account and hendle it.

    If pare <url, login> already exist then request to update password for pare.
    Else request password for new account.
    """
    locale = clients[message.chat.id].locale
    bw_client = clients[message.chat.id].get_bw()
    login = str(message.text)
    await state.update_data(login=login)
    data = await state.get_data()
    url = data["url"]

    bw_data = bw_client.search_items_with_uri_part(url)

    same_login = []

    for el in bw_data:
        if data["login"] == el["login"]["username"]:
            for j in el["login"]["uris"]:
                same_login.append(j["uri"])


    if url in same_login:
        await message.answer(_(locale, "For this website, an account with this login is already recorded.\n"))
        await state.clear()
        await main_menu(message)

    else:
        await message.answer(_(locale, "Enter the password for account on website {}\n").format(url)
                             + _(locale, "Login: {}").format(login))
        await state.set_state(Set_Password.password)
