import logging
import os

from aiogram import Bot, Router, types, F
from aiogram.types import FSInputFile
from aiogram.filters.command import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter


router = Router()
storage = MemoryStorage()


class Form(StatesGroup):
    faq = State()


@router.message(StateFilter(None))
async def init_handler(message: types.Message, bot: Bot, state: FSMContext):
    pass
    

@router.message(Command("start"))
async def handle_start_command(message: types.Message):
    pass


@router.message(F.voice)
async def handle_voice_message(message: types.Message, bot: Bot, state: FSMContext):
    pass
        
        
@router.message(F.text)
async def handle_text_message(message: types.Message, state: FSMContext):
    pass
    