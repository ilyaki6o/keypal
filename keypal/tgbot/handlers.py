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

from . import keyboards as kb

urls = ["www.google.com",
        "calendar.google.com",
        "music.google.com",
        "tasks.google.com",
        "youtube.google.com",
        "news.google.com",
        "market.google.com",
        "adskjdsa.google.com",
        "jhadsskj.google.com",
        "fdsakjdas.google.com",
        "akjoiqwio.google.com",
        ]

meneger = {"www.google.com": {"ilya": "askdjlashj2123"}}


router = Router()
bw = ''
url_column = 0
login_column = 0
chosen_urls = []
chosen_logins = []


class User(StatesGroup):
    client_id = State()
    client_secret = State()


class MasterP(StatesGroup):
    master_password = State()


class Password_flow(StatesGroup):
    url = State()
    login = State()
    password = State()
    work_type = State()


class Set_Password(StatesGroup):
    url = State()
    login = State()
    password = State()


################# Commands


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello, its KeyPal - telegram bot wrapper for Bitwarden password manager.")
    await message.answer("Do you already have a Bitwarden account?", reply_markup=kb.start)


################# Callback


@router.callback_query(F.data == "log_in")
async def log_in(call: CallbackQuery, state: FSMContext):
    await request_client_id(call.message, state)
    await call.answer('')


@router.callback_query(F.data == "registration")
async def registration(call: CallbackQuery):
    await call.message.answer("Let's set you up with a Bitwarden account."
                              + "To register an account on the Bitwarden website click on the button below.",
                              reply_markup=kb.reg_account)
    await call.message.answer("Click the button below when you register your account to log in.",
                              reply_markup=kb.log_in)
    await call.answer('')


@router.callback_query(F.data == "start_session")
async def master_password(call: CallbackQuery, state: FSMContext):
    await state.set_state(MasterP.master_password) 
    await call.message.answer("Please enter your master password")
    await call.answer('')

@router.callback_query(F.data == "get_password")
async def get_password(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Enter the url to search for the password")
    await state.set_state(Password_flow.url)
    await state.update_data(work_type=str(call.data))
    await call.answer('')


@router.callback_query(F.data == "update_password")
async def update_password(call: CallbackQuery, state: FSMContext):
    await call.message.answer("Enter the url to search for the password")
    await state.set_state(Password_flow.url)
    await state.update_data(work_type=str(call.data))
    await call.answer('')


@router.callback_query(F.data == "set_password")
async def set_password(call: CallbackQuery, state:FSMContext):
    await call.message.answer("Enter the address of the site for which you want to save the password")
    await state.set_state(Set_Password.url)
    await call.answer("")


@router.callback_query(F.data.startswith("url_"))
async def accept_url(call: CallbackQuery, state: FSMContext):
    correct_url = str(call.data)[4:]

    await state.update_data(url=correct_url)
    await state.set_state(Password_flow.login)
    await choose_login(call.message, state)
    await call.answer("")


@router.callback_query(F.data.startswith("login_"))
async def accept_login(call: CallbackQuery, state: FSMContext):
    correct_login = str(call.data)[6:]

    await state.update_data(login=correct_login)
    await check_work_type(call.message, state)
    await call.answer("")


@router.callback_query(F.data.startswith("next_"))
async def next_column(call: CallbackQuery):
    global chosen_urls, url_column, chosen_logins, login_column

    state = str(call.data)[5:]

    match state:
        case "url":
            url_column += 1
            await call.message.edit_text("Please select website", reply_markup=await kb.buttons_list(chosen_urls, url_column, "url"))
        case "login":
            login_column += 1
            await call.message.edit_text("Please select login", reply_markup=await kb.buttons_list(chosen_logins, login_column, "login"))

    await call.answer("")


@router.callback_query(F.data.startswith("prev_"))
async def prev_column(call: CallbackQuery):
    global chosen_urls, url_column, chosen_logins, login_column

    state = str(call.data)[5:]

    match state:
        case "url":
            url_column -= 1
            await call.message.edit_text("Please select website", reply_markup=await kb.buttons_list(chosen_urls, url_column, "url"))
        case "login":
            login_column -= 1
            await call.message.edit_text("Please select login", reply_markup=await kb.buttons_list(chosen_logins, login_column, "login"))

    await call.answer("")


@router.callback_query(F.data.startswith("update_exist_password_"))
async def chenge_exist_password(call: CallbackQuery, state: FSMContext):
    type_bt = str(call.data)[-3:]

    match type_bt:
        case "yes":
            await call.message.answer("Please enter new password")
            await state.set_state(Set_Password.password)
        case "_no":
            await call.message.edit_text("Adding a password is canceled")
            await state.clear()
            await main_menu(call.message)

    await call.answer("")


####### Func


async def start_session(message: Message):
    await message.answer("Click the button below to start new session", reply_markup=kb.new_session)


async def request_client_id(message: Message, state: FSMContext):
    await state.set_state(User.client_id) 
    await message.answer("Please enter your client_id")


async def main_menu(message: Message):
    await message.answer("Welcome to KeyPal", reply_markup=kb.main_menu)


############# States


@router.message(User.client_id)
async def request_client_secret(message: Message, state: FSMContext):
    await state.update_data(client_id=message.text)
    await state.set_state(User.client_secret)
    await message.answer("Please enter your client_secret")


@router.message(User.client_secret)
async def auth_check(message: Message, state: FSMContext):
    await state.update_data(client_secret=message.text)
    data = await state.get_data()

    await message.answer(f"Your client_id: {data['client_id']}\nYour client_secret: {data['client_secret']}")
    # try:
    #     bw = bitwd.BITWARDEN(data["client_id"], data["client_secret"])
    # except pex_exc.EOF:
    #     message.answer("Login or client_secret is wrong. Please try log in again.")
    #     await request_client_id(message, state)
    # else:
    
    await state.clear()
    await start_session(message)


@router.message(MasterP.master_password)
async def check_master_password(message: Message, state: FSMContext):
    await state.update_data(master_password=message.text)
    data = await state.get_data()

    await message.answer(f"Your master_password: {data['master_password']}")

    await state.clear()
    await main_menu(message)


@router.message(Password_flow.url)
async def choose_url(message: Message, state: FSMContext):
    global url_column, chosen_urls
    
    url = message.text
    cur_urls = urls
    chosen_urls = []
    url_column = 0

    for el in cur_urls:
        if str(url) in el:
            chosen_urls.append(el)

    chosen_urls = sorted(chosen_urls)

    if len(chosen_urls) == 0:
        await message.answer("There are no records for this website")
        await state.clear()
        await main_menu(message)
    elif len(chosen_urls) == 1:
        await message.answer("Selected website {}".format(chosen_urls[0]))
        await state.update_data(url=chosen_urls[0])
        await state.set_state(Password_flow.login)
        await choose_login(message, state)
    else:
        await message.answer("Please select website", reply_markup=await kb.buttons_list(chosen_urls, url_column, "url"))


async def choose_login(message: Message, state: FSMContext):
    global login_column, chosen_logins

    chosen_logins, login_column = [], 0
    data = await state.get_data()

    chosen_logins = ["ilya1337", "roman228", "igor322", "valera", "dimon", "barabashka"]

    chosen_logins = sorted(chosen_logins)
    await message.answer("Please select login", reply_markup=await kb.buttons_list(chosen_logins, login_column, "login"))


async def check_work_type(message: Message, state: FSMContext):
    password = "asdasdas123123asdasd"
    await state.update_data(password=password)
    data = await state.get_data()

    if data["work_type"] == "get_password":
        await send_password(message, state)
    elif data["work_type"] == "update_password":
        await message.answer("Please enter new password")
        await state.set_state(Password_flow.password)


async def send_password(message: Message, state: FSMContext):
    data = await state.get_data()

    res = "For website: {}\n\nLogin: <code>{}</code>\nPassword: <code>{}</code>".format(data["url"], data["login"], data["password"])

    await message.answer(res, parse_mode=ParseMode.HTML)
    await state.clear()
    await main_menu(message)


@router.message(Password_flow.password)
async def change_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await send_password(message, state)


@router.message(Set_Password.password)
async def set_new_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await send_password(message, state)


@router.message(Set_Password.url)
async def url_for_set(message: Message, state: FSMContext):
    url = str(message.text)

    if validators.url(url):
        url = urlparse(url).netloc
        url = '.'.join(url.split('.')[-2:])

    await state.update_data(url=url)
    
    await message.answer("Enter the login of the account on this website for which you want to save a password")
    await state.set_state(Set_Password.login)


@router.message(Set_Password.login)
async def login_for_set(message: Message, state: FSMContext):
    login = str(message.text)
    await state.update_data(login=login)
    data = await state.get_data()
    url = data["url"]

    if url in meneger and login in meneger[url]:
        await message.answer("For this website, an account with this login is already recorded.\n"
                             + "Would you like to update your password?", reply_markup=kb.update_exist_password)
    else:
        await message.answer("Enter the password for account on website {}\n".format(url)
                             + "Login: {}".format(login))
        await state.set_state(Set_Password.password)
