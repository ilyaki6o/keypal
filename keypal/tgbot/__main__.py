"""Main file of telegram bot."""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from . import handlers as hl

TOKEN = "7342917304:AAG0OneBgGCglwp07pD3TXw5tNPwMCf1E2o"

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    """Include routert and start bot."""
    dp.include_router(hl.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("exit")
