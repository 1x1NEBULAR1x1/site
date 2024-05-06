from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery
from config import HOST, REFERRAL_INFO, QUESTION1, QUESTION2, QUESTION3
from engine import DataBase
import keyboards as kb
from FSM import FSM
from aiogram.fsm.context import FSMContext

callbacks = Router()
'''
User menu---------------------------------------------------------------------------------------------------------------
'''
'''
Menu--------------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'start')
async def u_start(call: CallbackQuery, db: DataBase, state: FSMContext):
    user = await db.get_user(user_id=call.from_user.id)
    if user.banned:
        return
    await state.clear()
    await db.add_user(call.message)
    await call.message.edit_text(text='Добро пожаловать в бота',
                                reply_markup=await kb.start(user=user, key=user.can_create_links))
'''
Menu--------------------------------------------------------------------------------------------------------------------
'''
'''
Referral----------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'referral')
async def referral(call: CallbackQuery):
    if REFERRAL_INFO:
        await call.message.edit_text(text=f'{REFERRAL_INFO}', reply_markup=await kb.back_to_menu())
    else:
        await call.message.edit_text(text='Нет описания у реферальной программы', reply_markup=await kb.back_to_menu())


'''
Referral----------------------------------------------------------------------------------------------------------------
'''
'''
Chats-------------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'chats')
async def chats(call: CallbackQuery, db: DataBase):
    user = await db.get_user(user_id=call.from_user.id)
    if user.banned:
        await call.message.edit_text(text='Вы заблокированы')
        return
    await call.message.edit_text(text='Список чатов', reply_markup=await kb.chats())
'''
Chats-------------------------------------------------------------------------------------------------------------------
'''
'''
Questions---------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'questions')
async def questions(call: CallbackQuery, db: DataBase, state: FSMContext):
    user = await db.get_user(user_id=call.message.chat.id)
    if user.banned:
        await call.message.edit_text(text='Вы заблокированы')
        return
    text = f'Пройтите опрос для создания ссылок\n{QUESTION1 if QUESTION1 else QUESTION2 if QUESTION2 else QUESTION3}'
    await state.set_state(FSM.question_1 if QUESTION1 else FSM.question_2 if QUESTION2 else FSM.final_question)
    await state.update_data(message_id=call.message.message_id)
    await call.message.edit_text(text=text)
'''
Questions---------------------------------------------------------------------------------------------------------------
'''
'''
Link--------------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'my_links')
async def my_link(call: CallbackQuery, db: DataBase):
    user = await db.get_user(user_id=call.from_user.id)
    if user.banned:
        return
    keys = await db.get_user_keys(user_id=user.user_id)
    if not keys:
        await call.message.edit_text(text='Ссылки еще не созданы', reply_markup=await kb.my_link(status=False))
        return
    text, requestss = 'Ваши ссылки:\n\n', []
    for key in keys:
        requests, total = await db.get_requests_by_key(key=key.key), 0
        text += f'Ссылка: <code>https://{HOST}/{key.key}/</code>'
        if requests:
            requestss.append(requests)
            for request in requests:
                total += request.price
            text += f'\nВсего заявок: {len(requests)}\nОбщая сумма: {total}\n\n'
    await call.message.edit_text(text=text, reply_markup=await kb.my_link(status=not not requestss))
@callbacks.callback_query(F.data == 'create_link')
async def create_link(call: CallbackQuery, db: DataBase):
    key = await db.add_key(owner_id=call.message.chat.id)
    await call.message.edit_text(text=f'Ссылка создана\nСсылка: <code>https://{HOST}/{key}/</code>',
                                 reply_markup=await kb.back_to_links())

'''
Link--------------------------------------------------------------------------------------------------------------------
'''
'''
User menu---------------------------------------------------------------------------------------------------------------
'''
'''
Admin menu--------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'a_menu')
async def a_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text='Меню администратора', reply_markup=await kb.a_menu())
@callbacks.callback_query(F.data == 'a_stats')
async def a_stats(call: CallbackQuery, db: DataBase):
    requests = await db.get_requests()
    total, unkeyed,  users_, named, text = 0, 0, {}, {}, ''
    for request in requests:
        total += request.price
        if request.key:
            if request.key not in users_.keys():
                users_.update({request.key: 0})
            else:
                users_[request.key] += request.price
        else:
            unkeyed += request.price
    for key in await db.get_keys():
        user = await db.get_user(key.owner_id)
        if user:
            named.update({user.user_id: users_[key.key]})
    for user_id in named.keys():
        user = await db.get_user(user_id=user_id)
        text += f'{"@"+user.username if user.username else user.first_name}: {named[user]}\n'
    text += f'Общая сумма: {total}\nБез приглашения: {unkeyed}\n'
    text += f'Всего заявок: {len(requests)}'
    await call.message.edit_text(text=text, reply_markup=await kb.a_stats())
'''
Link requests-----------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data.startswith('a_c_create_link'))
async def a_c_create_link(call: CallbackQuery, db: DataBase, bot: Bot):
    user = await db.get_user(user_id=int(call.data.split('_')[4]))
    if user.banned:
        await call.message.edit_text(text='Пользователь заблокирован, необходимо его разблокировать, прежде чем '
                                          'создавать ссылку', reply_markup=await kb.back_to_menu())
        return
    await db.user_can_create_links(user_id=user.user_id, status=True)
    await call.message.edit_text(text=f'Пользователь получил право на создание ссылок',
                                 reply_markup=await kb.back_to_menu())
    for msg in await db.get_messages(chat_id=user.user_id):
        try:
            await bot.delete_message(chat_id=user.user_id, message_id=msg.message_id)
            await db.delete_message(id_=msg.id)
        except TelegramBadRequest:
            pass
    msg = await bot.send_message(chat_id=user.user_id, text=f'Вы получили право на создание ссылок',
                                 reply_markup=await kb.back_to_menu())
    await db.add_message(chat_id=user.user_id, message_id=msg.message_id)
@callbacks.callback_query(F.data.startswith('a_d_create_link'))
async def a_d_create_link(call: CallbackQuery, db: DataBase, bot: Bot):
    user = await db.get_user(user_id=int(call.data.split('_')[4]))
    await call.message.edit_text(text=f'Заявка на получение прав на создание ссылок отклонена',
                                 reply_markup=await kb.back_to_menu())
    for msg in await db.get_messages(chat_id=user.user_id):
        try:
            await bot.delete_message(chat_id=user.user_id, message_id=msg.message_id)
            await db.delete_message(id_=msg.id)
        except TelegramBadRequest:
            pass
    msg = await bot.send_message(chat_id=user.user_id, text=f'Администратор отклонил заявку на получние прав на '
                                                            f'создание ссылок',
                                 reply_markup=await kb.back_to_menu())
    await db.add_message(chat_id=user.user_id, message_id=msg.message_id)



'''
Link requests-----------------------------------------------------------------------------------------------------------
'''



'''
Users-------------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data == 'a_users')
async def a_users(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(text='Меню взаимодействия с пользователями', reply_markup=await kb.a_users())
@callbacks.callback_query(F.data == 'a_users_find')
async def a_users_find(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(text='Введите имя, ник или ID пользователя', reply_markup=await kb.a_users_find())
    await state.update_data(message_id=call.message.message_id)
    await state.set_state(FSM.find_user)

@callbacks.callback_query(F.data.startswith('a_users_list_'))
async def a_users_list(call: CallbackQuery, db: DataBase):
    users = await db.get_users()
    await call.message.edit_text(text=f'Список пользователей\nВсего: {len(users)} пользователей',
                                 reply_markup=await kb.a_users_list(page=int(call.data.split('_')[2]) if
                                 len(call.data.split('_')) == 3 else 0, users=users))
'''
Users-------------------------------------------------------------------------------------------------------------------
'''
'''
User--------------------------------------------------------------------------------------------------------------------
'''
'''
User status-------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data.startswith('a_user_requests_'))
async def a_user_requests(call: CallbackQuery, db: DataBase):
    user_id = int(call.data.split('_')[3])
    keys, text = await db.get_user_keys(user_id=user_id), ''
    if not keys:
        text = 'У пользователя нет ссылок'
    for key in keys:
        requests, total = await db.get_requests_by_key(key=key.key), 0
        for request in requests:
            total += request.price
        text += f'Ссылка: {key.key}\nВсего заявок: {len(requests)}\nОбщая сумма: {total}\n\n'
    if len(text) > 4096:
        text = text[:4096]
    await call.message.edit_text(text=text, reply_markup=await kb.a_back_to_user(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_ban_'))
async def a_user_ban(call: CallbackQuery):
    user_id = int(call.data.split('_')[3])
    await call.message.edit_text(text='Подтвердите действие', reply_markup=await kb.a_user_ban(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_c_ban_'))
async def a_user_c_ban(call: CallbackQuery, db: DataBase):
    user_id = int(call.data.split('_')[4])
    await db.update_user_status(user_id=user_id, status=True)
    await call.message.edit_text(text='Пользователь заблокирован',
                                 reply_markup=await kb.a_back_to_user(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_unban_'))
async def a_user_unban(call: CallbackQuery):
    user_id = int(call.data.split('_')[3])
    await call.message.edit_text(text='Подтвердите действие', reply_markup=await kb.a_user_unban(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_c_unban_'))
async def a_user_c_unban(call: CallbackQuery, db: DataBase):
    user_id = int(call.data.split('_')[4])
    await db.update_user_status(user_id=user_id, status=False)
    await call.message.edit_text(text='Пользователь разблокирован',
                                 reply_markup=await kb.a_back_to_user(user_id=user_id))
'''
User status-------------------------------------------------------------------------------------------------------------
'''
'''
User key---------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data.startswith('a_user_delete_c_key_'))
async def a_user_delete_c_key(call: CallbackQuery, db: DataBase):
    user_id = int(call.data.split('_')[5])
    await db.user_can_create_links(user_id=user_id, status=False)
    await db.delete_keys(user_id=user_id)
    await call.message.edit_text(text='Пользователь теперь не может создавать ссылки, все прошлые ссылки удалены',
                                 reply_markup=await kb.a_back_to_user(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_delete_key_'))
async def a_user_delete_key(call: CallbackQuery):
    user_id = int(call.data.split('_')[4])
    await call.message.edit_text(text='Подтвердите действие', reply_markup=await kb.a_user_delete_key(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_create_c_key_'))
async def a_user_create_c_key(call: CallbackQuery, db: DataBase):
    user_id = int(call.data.split('_')[5])
    await db.user_can_create_links(user_id=user_id, status=True)
    await call.message.edit_text(text=f'Пользователь теперь может создавать ссылки',
                                 reply_markup=await kb.a_back_to_user(user_id=user_id))
@callbacks.callback_query(F.data.startswith('a_user_create_key_'))
async def a_user_create_key(call: CallbackQuery):
    user_id = int(call.data.split('_')[4])
    await call.message.edit_text(text='Подтвердите действие', reply_markup=await kb.a_user_create_key(user_id=user_id))
'''
User key---------------------------------------------------------------------------------------------------------------
'''
'''
User menu---------------------------------------------------------------------------------------------------------------
'''
@callbacks.callback_query(F.data.startswith('a_user_'))
async def a_user(call: CallbackQuery, db: DataBase):
    user_id = int(call.data.split('_')[2])
    user = await db.get_user(user_id=user_id)
    key = await db.get_key(user_id=user_id)
    await call.message.edit_text(text=f'ID: {user.user_id}\n'
                                      f'Имя пользователя: {user.first_name}\n'
                                      f'Ник пользователя: @{user.username}\n'
                                      f'Дата регистрации: {user.created.date()}\n'
                                      f'Последняя активность: {user.updated.date()}\n'
                                      f'Статус: {"Забанен" if user.banned else "Не забанен"}\n'
                                      f'Ссылки: {"Имеет право на создание ссылок" if user.can_create_links else "Нет прав на создание ссылок"}',
                                 reply_markup=await kb.a_user(user=user, key=user.can_create_links))
'''
User menu---------------------------------------------------------------------------------------------------------------
'''
'''
User--------------------------------------------------------------------------------------------------------------------
'''
'''
Admin menu--------------------------------------------------------------------------------------------------------------
'''