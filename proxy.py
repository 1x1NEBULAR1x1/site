from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware
from config import DATABASE_URL
from engine import DataBase
import jinja2
import requests

db = DataBase(database_url=DATABASE_URL)
app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.get('/')
async def link(key: str | None = None):
    return requests.get('http://host-195-2-85-241.hosted-by-vdsina.ru:8000/'+("?key="+key if key else ""))

@app.post("/")
async def receive_data(
    key: Annotated[str, Form()] = None,
    caption: Annotated[str, Form()] = None,
    photo: UploadFile = File(...),
    departure_value: str = Form(...),
    destination_value: str = Form(...),
    price: float = Form(...)
):
    # Преобразуем данные из UploadFile в bytes
    photo_bytes = await photo.read()

    # Формируем данные для отправки
    payload = {
        'key': key,
        'caption': caption,
        'photo': photo_bytes,
        'departure_value': departure_value,
        'destination_value': destination_value,
        'price': price
    }
    # Отправляем данные на указанный URL
    target_url = 'http://host-195-2-85-241.hosted-by-vdsina.ru:8000/' + ("?key="+key if key else "")
    try:
        response = requests.post(target_url, data=payload)
        response.raise_for_status()  # Проверяем статус ответа
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке запроса: {e}")

    # Возвращаем ответ
    return response.json()

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)