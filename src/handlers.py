import logging

from config import DEBUG
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import Bot, Router, types, F
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter
from redis.asyncio.client import Redis
from aiogram.fsm.storage.redis import RedisStorage


router = Router()
storage = None
if DEBUG:
    logging.info("Using redis as storage")
    redis_client = Redis()
    storage = RedisStorage(redis_client)
else:
    logging.info("Using memory storage as storage")
    storage = MemoryStorage()


class Form(StatesGroup):
    company_name = State()
    company_url = State()
    default = State()
    faq = State()
    settings = State()
    auth = State()


######
# init
@router.message(Command("start"))
async def handle_start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Let's start from the beginning", reply_markup=ReplyKeyboardRemove())
    await handle_null(message, state)
    
    
@router.message(StateFilter(None))
async def handle_null(message: types.Message, state: FSMContext):
    await state.set_state(Form.company_name)
    await message.answer("Welcome! Let's come to setup process")
    await message.answer("Please, enter the company name:")


@router.message(Form.company_name, F.text)
async def handle_company_name(message: types.Message, state: FSMContext, bot: Bot):
    company_name = message.text
    await state.update_data(company_name=company_name)
    # TODO
    try:
        await bot.set_my_name(f"{company_name} FAQ")
    except Exception as e: 
        logging.warning(f"Error changing bot name: {str(e)}")
    
    if (await state.get_data()).get('auth', True):
        await state.set_state(Form.company_url)
        await message.answer("Please, enter the company url:", reply_markup=ReplyKeyboardRemove())
    else:
        await state.set_state(Form.settings)


@router.message(Form.company_url, F.text)
async def handle_company_url(message: types.Message, state: FSMContext):
    await state.update_data(company_url=message.text)
    
    if (await state.get_data()).get('auth', True):
        await state.set_state(Form.default)
        await state.update_data(auth=False)
        await message.answer("Setup succeeded!", reply_markup=ReplyKeyboardRemove())
        await message.answer("You can either parse url and then ask bot about a company or fix something in settings")
        await handle_default(message, state)
    else: 
        await state.set_state(Form.settings)
    

#########
# default    
@router.message(Form.default, F.text.lower() == "parse url")
async def handle_parse_url(message: types.Message, state: FSMContext):
    # TODO parsing url
    await message.answer("Url parsed successfully! You can go FAQ now", reply_markup=ReplyKeyboardRemove())
    await handle_default(message, state)
    
       
@router.message(Form.default, F.text.lower() == "faq")
async def handle_faq(message: types.Message, state: FSMContext):
    await state.set_state(Form.faq)
    await message.answer("Ask questions!", reply_markup=ReplyKeyboardRemove())
    await message.answer("Use /back to leave")


@router.message(Form.default, F.text.lower() == "settings")
async def handle_to_settings(message: types.Message, state: FSMContext):
    await state.set_state(Form.settings)
    await handle_settings(message, state)
       
       
@router.message(Form.default)
async def handle_default(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[

            [KeyboardButton(text="Parse URL"), KeyboardButton(text="FAQ")],
            [KeyboardButton(text="Settings")]
        ],
        resize_keyboard=True
    )
    await message.answer(text="What do you want to do?", reply_markup=keyboard)
 

#####
# faq
@router.message(Form.settings, F.text.lower() == "back to main menu")
@router.message(Form.faq, Command("back"))
@router.message(Form.faq, F.text.lower() == "back")
async def handle_back_to_main_menu(message: types.Message, state: FSMContext):
    await state.set_state(Form.default)
    
    await handle_default(message, state)
    
    
@router.message(Form.faq, F.voice)
async def handle_voice_message(message: types.Message, state: FSMContext):
    # TODO
    pass
        
        
@router.message(Form.faq, F.text)
async def handle_text_message(message: types.Message, state: FSMContext):
    # TODO
    pass
    
    
##########
# settings 
@router.message(Form.settings, F.text.lower() == "change name")
async def handle_change_name(message: types.Message, state: FSMContext, bot: Bot):
    await state.set_state(Form.company_name)
    await message.answer("Please, enter new company name:")
    await handle_company_name(message, state, bot)
    
       
@router.message(Form.settings, F.text.lower() == "change url")
async def handle_change_url(message: types.Message, state: FSMContext):
    await state.set_state(Form.company_url)
    await message.answer("Please, enter new company url:")
    await handle_company_url(message, state)
    
    
@router.message(Form.settings)
async def handle_settings(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Change name"), KeyboardButton(text="Change URL")],
            [KeyboardButton(text="Back to main menu")]
        ],
        resize_keyboard=True
    )
    await message.answer(text="Here we go", reply_markup=keyboard)