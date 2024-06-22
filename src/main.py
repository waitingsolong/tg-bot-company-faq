import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.utils import executor

from config import config
from handlers import router,storage
from logs import init_logs


async def main(): 
    bot = Bot(token=config.telegram_token.get_secret_value())
    dp = Dispatcher(storage=storage)
    dp.include_router(router)


    logging.info('Starting polling...')
    try:
        await bot.delete_webhook()
        await executor.start_polling(dp, skip_updates=True)
    finally:
        await storage.close()
        await bot.session.close()
        logging.info('Shutdown complete.')
    

if __name__ == '__main__':
    init_logs()

    asyncio.run(main())
