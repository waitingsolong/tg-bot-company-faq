import logs
import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN
from handlers import router,storage


async def main(): 
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(router)


    logging.info('Starting polling...')
    try:
        await bot.delete_webhook()
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await dp.storage.close()
        await bot.session.close()
        logging.info('Shutdown complete.')
    

if __name__ == '__main__':
    asyncio.run(main())
