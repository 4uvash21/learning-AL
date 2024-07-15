from aiogram import types, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart, StateFilter, CommandObject, CREATOR
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from database import quiz_data
from service import generate_options_keyboard, get_question, new_quiz, get_quiz_index, get_correct_num, update_ind_and_corr

router = Router()


async def answer(callback, is_right):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    user_id = callback.from_user.id
    question_index = await get_quiz_index(user_id)
    correct_num = await get_correct_num(user_id)

    if is_right:
        await callback.message.answer("Верно!")
        await update_ind_and_corr(user_id, question_index + 1, correct_num + 1)
    else:
        correct_answer = quiz_data[question_index]["options"][quiz_data[question_index]["correct_option"]]
        await callback.message.answer(f"Неправильно. Правильный ответ: {correct_answer}")
        await update_ind_and_corr(user_id, question_index + 1, correct_num)

    if (question_index + 1) < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer(f"Квиз завершен! Ваш результат: {await get_correct_num(user_id)} из {await get_quiz_index(user_id)}")


@router.callback_query(F.data == "right_answer")
async def right_answer(callback: types.CallbackQuery):
    await answer(callback, True)


@router.callback_query(F.data == "wrong_answer")
async def right_answer(callback: types.CallbackQuery):
    await answer(callback, False)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)