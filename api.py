import os
from PIL import Image
from typing import Annotated
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from fastapi import FastAPI, Form, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from config import BOT_TOKEN, DATABASE_URL
from engine import DataBase
import uvicorn
import jinja2

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
db = DataBase(database_url=DATABASE_URL)
app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.add_middleware


@app.post('/')
async def send(departure_value: Annotated[str, Form()],
               destination_value: Annotated[str, Form()],
               price: Annotated[float, Form()],
               key: Annotated[str, Form()] = None,
               caption: Annotated[str, Form()] = None,
               photo: UploadFile = File(...)):
    if key:
        key = await db.get_key(key=key)
        if key:
            key = key.key
    request = await db.add_request(key=key, caption=caption, departure_value=departure_value,
                                   destination_value=destination_value, price=price)
    if not os.path.exists('./images/'):
        os.mkdir('./images/')
    image = Image.open(photo.file)
    if key:
        if not os.path.exists('./images/' + str(key)):
            os.mkdir('./images/' + str(key))
        image.save('./images/' + str(key) + '/' + str(request.request_id) + '.png', 'PNG')
    else:
        if not os.path.exists('.images/all'):
            os.mkdir('./images/all')
        image.save('./images/all/' + str(request.request_id) + '.png', 'PNG')
    return {'status': 'ok', 'request_id': request.request_id}


@app.get('/')
async def link(key: str | None = None):
    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))
    template = jinja.get_template('index.html')
    if not await db.get_key(key=key):
        return HTMLResponse(template.render(key=''))
    template = template.render(key=key)
    return HTMLResponse(template)







if __name__ == '__main__':
    uvicorn.run('api:app', host='localhost', port=8080, reload=True)