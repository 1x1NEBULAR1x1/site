import uvicorn
from aiogram import Bot, Dispatcher
import asyncio
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN, DATABASE_URL
from engine import DataBase
from handlers import handlers
from callbacks import callbacks
async def start_bot():
    try:
        await db.process_scheme()
    except Exception as e:
        print(e)
    finally:
        print('Bot started')
async def stop_bot():
    print('Bot stopped')
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
db = DataBase(database_url=DATABASE_URL)
dp = Dispatcher()
dp.startup.register(start_bot)
dp.shutdown.register(stop_bot)
dp.include_routers(handlers, callbacks)
async def bot_def():
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, db=db)
    finally:
        await bot.close()
async def api_def():
    config = uvicorn.Config('api:app', port=8000, host='localhost')
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == '__main__':
    try:
        loop = asyncio.new_event_loop()
        loop.create_task(bot_def())
        loop.create_task(api_def())
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
