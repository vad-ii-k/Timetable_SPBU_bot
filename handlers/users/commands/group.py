from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keyboards.inline.student_navigaton_buttons import create_study_divisions_keyboard
from loader import dp
from utils.timetable.api import get_study_divisions


@dp.message_handler(commands='group', state="*")
async def bot_group_command(message: Message, state: FSMContext):
    await state.finish()
    answer = await message.answer("Выберите направление для поиска группы: ")
    study_divisions = await get_study_divisions()
    await answer.edit_reply_markup(reply_markup=await create_study_divisions_keyboard(study_divisions))
