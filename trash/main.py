import logging
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import Command

from handlers import start, process_start_tunnel, process_stop_tunnel, process_tunnel_status
from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

def register_handlers(dp: Dispatcher):
    dp.message.register(start, Command('start'))
    dp.message.register(process_start_tunnel, Command('start_tunnel'))
    dp.message.register(process_stop_tunnel, Command('stop_tunnel'))
    dp.message.register(process_tunnel_status, Command('status'))

async def main():
    logging.basicConfig(level=logging.INFO)
    register_handlers(dp)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
