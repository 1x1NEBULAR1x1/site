from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton, InlineKeyboardBuilder
from config import ADMINS_IDS, ADMIN_USERNAME, CHATS
from scheme import User, Key
from typing import Sequence

async def start(user: User, key: str | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if key:
        kb.row(InlineKeyboardButton(text='Мои ссылки', callback_data='my_links'))
        kb.row(InlineKeyboardButton(text='Реферальная программа', callback_data='referral'))
        kb.row(InlineKeyboardButton(text='Чаты', callback_data='chats'))
    else:
        kb.row(InlineKeyboardButton(text='Пройти опрос заново', callback_data='questions'))
    if user.user_id in ADMINS_IDS:
        kb.row(InlineKeyboardButton(text='Меню администратора', callback_data='a_menu'))
    return kb.as_markup()
async def my_link(status: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Создать ссылку', callback_data='create_link'))
    if status:
        kb.row(InlineKeyboardButton(text='Запросить выплату', url=f'https://t.me/{ADMIN_USERNAME}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='start'))
    return kb.as_markup()
async def chats() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for chat in CHATS:
        kb.row(InlineKeyboardButton(text=chat.get('chat_name'), url=chat.get('chat_link')))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='start'))
    return kb.as_markup()

async def back_to_links() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Назад', callback_data='my_links'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='start'))
    return kb.as_markup()
async def a_create_link(user: User) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Принять заявку', callback_data=f'a_c_create_link_{user.user_id}'))
    kb.row(InlineKeyboardButton(text='Отклонить заявку', callback_data=f'a_d_create_link_{user.user_id}'))
    if user.username:
        kb.row(InlineKeyboardButton(text=f'Перейти в чат', callback_data=f'https://t.me/{user.username}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def back_to_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Меню', callback_data='start'))
    return kb.as_markup()
async def a_stats() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Назад', callback_data='a_menu'))
    return kb.as_markup()

async def a_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Пользователи', callback_data='a_users'))
    kb.row(InlineKeyboardButton(text='Статистика', callback_data='a_stats'))
    kb.row(InlineKeyboardButton(text='Перейти в меню пользователя', callback_data='start'))
    return kb.as_markup()
async def a_users() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Поиск пользователя', callback_data='a_users_find'))
    kb.row(InlineKeyboardButton(text='Список пользователей', callback_data='a_users_list_0'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='a_menu'))
    return kb.as_markup()

async def a_users_find() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Назад', callback_data='a_users'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def a_users_list(users: Sequence[User], page: int = 0) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    users_len = len(users)
    users = users[page*45:page*45+45]
    for user in users:
        kb.row(InlineKeyboardButton(text=f'{user.first_name} - @{user.username}',
                                    callback_data=f'a_user_{user.user_id}'))
    if page > 0 and users_len > 45 * (page+1):
        kb.row(InlineKeyboardButton(text='◀', callback_data=f'a_users_list_{page-1}'),
               InlineKeyboardButton(text='▶', callback_data=f'a_users_list_{page+1}'))
    elif users_len > 45 * (page+1):
        kb.row(InlineKeyboardButton(text='▶', callback_data=f'a_users_list_{page+1}'))
    elif page > 0:
        kb.row(InlineKeyboardButton(text='◀', callback_data=f'a_users_list_{page-1}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='a_users'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def a_user(user: User, key: Key | None = None) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if key:
        kb.row(InlineKeyboardButton(text='Статистика', callback_data=f'a_user_requests_{user.user_id}'))
        kb.row(InlineKeyboardButton(text='Запретить создание ссылок',
                                    callback_data=f'a_user_delete_key_{user.user_id}'))
    else:
        kb.row(InlineKeyboardButton(text='Разрешить создание ссылок',
                                    callback_data=f'a_user_create_key_{user.user_id}'))
    if user.username:
        kb.row(InlineKeyboardButton(text=f'Перейти в чат', url=f'https://t.me/{user.username}'))
    if not user.banned:
        kb.row(InlineKeyboardButton(text='Заблокировать', callback_data=f'a_user_ban_{user.user_id}'))
    else:
        kb.row(InlineKeyboardButton(text='Разблокировать', callback_data=f'a_user_unban_{user.user_id}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='a_users'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def a_user_delete_key(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Запретить создание ссылок', callback_data=f'a_user_delete_c_key_{user_id}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data=f'a_user_{user_id}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def a_user_create_key(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Разрешить создание ссылок', callback_data=f'a_user_create_c_key_{user_id}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data=f'a_user_{user_id}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()


async def a_user_ban(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Заблокировать пользователя', callback_data=f'a_user_c_ban_{user_id}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data=f'a_user_{user_id}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()

async def a_user_unban(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Разблокировать пользователя', callback_data=f'a_user_c_unban_{user_id}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data=f'a_user_{user_id}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def a_back_to_user(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Назад', callback_data=f'a_user_{user_id}'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()
async def a_go_to_user(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Перейти к пользователю', callback_data=f'a_user_{user_id}'))
    kb.row(InlineKeyboardButton(text='Назад', callback_data='a_users'))
    kb.row(InlineKeyboardButton(text='Меню', callback_data='a_menu'))
    return kb.as_markup()