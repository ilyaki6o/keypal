# from ..bitwarden import Bitwarden as bitwd
# from pexpect import exceptions as pex_exc

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import keyboards as kb

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


class Get_Password(StatesGroup):
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
    await state.set_state(Get_Password.url)
    await call.answer('')


@router.callback_query(F.data.startswith("url_"))
async def accept_url(call: CallbackQuery, state: FSMContext):
    correct_url = str(call.data)[4:]

    await state.update_data(url=correct_url)
    await call.message.answer("Enter login from your account")
    await state.set_state(Get_Password.login)
    await call.answer("")


@router.callback_query(F.data.startswith("next_"))
async def next_column(call: CallbackQuery):
    global chosen_urls, url_column, chosen_logins, login_column

    state = str(call.data)[5:]

    match state:
        case "url":
            url_column += 1
            await call.message.edit_text("Please select website", reply_markup=await kb.select_url(chosen_urls, url_column))
        case "login":
            pass

    await call.answer("")


@router.callback_query(F.data.startswith("prev_"))
async def prev_column(call: CallbackQuery):
    global chosen_urls, url_column, chosen_logins, login_column

    state = str(call.data)[5:]

    match state:
        case "url":
            url_column -= 1
            await call.message.edit_text("Please select website", reply_markup=await kb.select_url(chosen_urls, url_column))
        case "login":
            pass

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


@router.message(Get_Password.url)
async def choose_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    
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
        await message.answer("Enter login from your account")
        await state.set_state(Get_Password.login)
    else:
        await message.answer("Please select website", reply_markup=await kb.select_url(chosen_urls, url_column))


@router.message(Get_Password.login)
async def choose_login(message: Message, state: FSMContext):
    await message.answer("Im in login state")
