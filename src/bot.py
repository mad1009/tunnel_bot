import asyncio
from aiogram import Bot, Dispatcher
from handlers import tunnel_handlers
from config import TELEGRAM_BOT_TOKEN
import logging

async def main():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(tunnel_handlers.router) # add more routers here
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

# Entry point
if __name__ == "__main__":
# Basic configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

    asyncio.run(main())
