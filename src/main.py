import logs
import asyncio
import logging

from aiogram import Bot, Dispatcher
from config import TELEGRAM_BOT_TOKEN
from config import OPENAI_API_KEY
from openai_client.client import OpenAIClient
from app.app import App
import globals
    

async def main():
    global openai_client 
    openai_client = OpenAIClient(api_key=OPENAI_API_KEY)
    
    globals.app = App(openai_client)
        
    from handlers import router,storage
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
