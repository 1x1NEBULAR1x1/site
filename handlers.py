from aiogram import Bot, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, BufferedInputFile
from engine import DataBase
from aiogram.filters import CommandStart, Command
import keyboards as kb
from FSM import FSM
from aiogram.fsm.context import FSMContext
from config import ADMINS_IDS, QUESTION2, QUESTION3, QUESTION1, TOP_IMG

handlers = Router()
'''
Command start-----------------------------------------------------------------------------------------------------------
'''
@handlers.message(CommandStart())
async def start(message: Message, db: DataBase, state: FSMContext, bot: Bot):
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    for msg in await db.get_messages(chat_id=message.chat.id):
        try:
            await bot.delete_message(message_id=msg.message_id, chat_id=msg.chat_id)
            await db.delete_message(id_=msg.id)
        except TelegramBadRequest:
            pass
    await state.clear()
    await db.add_user(message=message)
    user = await db.get_user(user_id=message.from_user.id)
    if user.banned:
        msg = await message.answer(text='Вы заблокированы')
        await db.add_message(message_id=msg.message_id, chat_id=msg.chat.id)
        return
    if user.can_create_links:
        msg = await message.answer(text='Добро пожаловать в бота',
                             reply_markup=await kb.start(user=user, key=user.can_create_links))
        await db.add_message(message_id=msg.message_id, chat_id=msg.chat.id)
        return
    text = 'Добро пожаловать в бота!\nПройдите опрос для создания ссылок'
    if QUESTION1:
        text += f'\n{QUESTION1}'
        await state.set_state(FSM.question_1)
    elif QUESTION2:
        text += f'\n{QUESTION2}'
        await state.set_state(FSM.question_2)
    elif QUESTION3:
        text += f'\n{QUESTION3}'
        await state.set_state(FSM.final_question)
    msg = await message.answer(text=text)
    await db.add_message(message_id=msg.message_id, chat_id=message.chat.id)
    await state.update_data(message_id=msg.message_id)
'''
Command start-----------------------------------------------------------------------------------------------------------
'''
'''
Command changehost------------------------------------------------------------------------------------------------------
'''


'''
Command top-------------------------------------------------------------------------------------------------------------
'''
@handlers.message(Command(commands=['top']))
async def top(message: Message, db: DataBase):
    users, all_ = [], 0
    for key in await db.get_keys():
        total = 0
        for request in await db.get_requests_by_key(key=key.key):
            total += request.price
        all_ += total
        users.append({'key': key.key, 'total': total})
    users.sort(key=lambda x: x.get('total'), reverse=True)
    users = users[:10]
    text = 'Топ пользователей\n\n'
    for usr in users:
        key = await db.get_key(key=usr.get('key'))
        user = await db.get_user(user_id=key.owner_id)
        text += f'{user.username} - {usr.get("total")}\n'
    text += f'\nВсего: {all_}'
    await message.answer_photo(photo=BufferedInputFile.from_file(TOP_IMG, 'top_image'),
                               caption=text)
'''
Command top-------------------------------------------------------------------------------------------------------------
'''
'''
Find user---------------------------------------------------------------------------------------------------------------
'''
@handlers.message(FSM.find_user)
async def find_user(message: Message, bot: Bot, db: DataBase, state: FSMContext):
    data = await state.get_data()
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if not message.text:
        await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                    text='Сообщение не содержит текст\nВведите имя, ник или ID пользователя',
                                    reply_markup=await kb.a_users_find())
        await state.set_state(FSM.find_user)
        return
    user = await db.find_user(text=message.text)
    if not user:
        await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                    text='Пользователь не найден\nВведите имя, ник или ID пользователя',
                                    reply_markup=await kb.a_users_find())
        await state.set_state(FSM.find_user)
        return
    await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                text=f'Пользователь найден!', reply_markup=await kb.a_go_to_user(user_id=user.user_id))
'''
Find user---------------------------------------------------------------------------------------------------------------
'''
'''
Questions---------------------------------------------------------------------------------------------------------------
'''
@handlers.message(FSM.question_1)
async def question_1(message: Message, bot: Bot, state: FSMContext, db: DataBase):
    data = await state.get_data()
    user = await db.get_user(user_id=message.from_user.id)
    if user.banned:
        return
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    if not message.text:
        await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                    text=f'Сообщение не содержит текст\n{QUESTION1}')
        await state.set_state(FSM.question_1)
        return
    await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id, text=f'{QUESTION2}')
    await state.update_data(question_1=message.text)
    await state.set_state(FSM.question_2)
@handlers.message(FSM.question_2)
async def question_2(message: Message, bot: Bot, state: FSMContext):
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    data = await state.get_data()
    if not message.text:
        await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                    text=f'Сообщение не содержит текст\n{QUESTION2}')
        await state.set_state(FSM.question_2)
        return
    await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id, text=f'{QUESTION3}')
    await state.update_data(question_2=message.text)
    await state.set_state(FSM.final_question)
@handlers.message(FSM.final_question)
async def final(message: Message, bot: Bot, state: FSMContext, db: DataBase):
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    data = await state.get_data()
    user = await db.get_user(user_id=message.from_user.id)
    if not message.text:
        await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                    text=f'Сообщение не содержит текст\n{QUESTION3}')
        await state.set_state(FSM.final_question)
        return
    if user.banned:
        return
    await bot.edit_message_text(message_id=data['message_id'], chat_id=message.chat.id,
                                reply_markup=await kb.back_to_menu(),
                                text=f'Администратор вскоре рассмотрит вашу заявку')
    await state.clear()
    text = 'Пользователь отправил заявку на получение права на создание ссылок\n'
    if QUESTION1:
        text += f'{QUESTION1}: \n{data["question_1"]}\n'
    if QUESTION2:
        text += f'{QUESTION2}: \n{data["question_2"]}\n'
    if QUESTION3:
        text += f'{QUESTION3}: \n{message.text}'
    for admin in ADMINS_IDS:
        try:
            for msg in await db.get_messages(chat_id=admin):
                await bot.delete_message(chat_id=admin, message_id=msg.message_id)
                await db.delete_message(id_=msg.id)
        except TelegramBadRequest:
            pass
        try:
            await bot.send_message(admin, text=text, reply_markup=await kb.a_create_link(user=user))
        except TelegramBadRequest:
            pass