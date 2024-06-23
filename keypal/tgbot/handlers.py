# from ..bitwarden import Bitwarden as bitwd
# from pexpect import exceptions as pex_exc

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import keyboards as kb


router = Router()
bw = ''


class User(StatesGroup):
    client_id = State()
    client_secret = State()

# class MasterP(StatesGroup):
#     master_password = State()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("Hello, its KeyPal - telegram bot wrapper for Bitwarden client_secret manager.")
    await message.answer("Do you already have a Bitwarden account?", reply_markup=kb.start)


@router.callback_query(F.data == "log_in")
async def log_in(call: CallbackQuery, state: FSMContext):
    await call.answer('')
    await request_client_id(call.message, state)


@router.callback_query(F.data == "registration")
async def registration(call: CallbackQuery):
    await call.answer('')
    await call.message.answer("Let's set you up with a Bitwarden account."
                              + "To register an account on the Bitwarden website click on the button below.",
                              reply_markup=kb.reg_account)
    await call.message.answer("Click the button below when you register your account to log in.",
                              reply_markup=kb.log_in)


# @router.callback_query(F.data == "start_session")
# async def master_password(call: CallbackQuery, state: FSMContext):
#     await state.set_state(MasterP.master_password) 
#     await call.answer('')
#     await call.message.answer("Please enter your master password")


# async def start_session(message: Message):
#     await message.answer("Click the button below to start new session", reply_markup=kb.new_session)


async def request_client_id(message: Message, state: FSMContext):
    await state.set_state(User.client_id) 
    await message.answer("Please enter your client_id")


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
    # await start_session(message)


# @router.message(MasterP.master_password)
# async def check_master_password(message: Message, state: FSMContext):
#     await state.update_data(master_password=message.text)
#     data = await state.get_data()
#
#     await message.answer(f"Your master_password: {data['master_password']}")
#
#     await state.clear()
