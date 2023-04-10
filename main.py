from fastapi import FastAPI, Request, Body,HTTPException,UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import configparser
import os
import database

try:
    # получение конфигов
    config = configparser.ConfigParser()
    config.read("./settings.ini")
    host = str(config["COMMON"]["host"])
    port = int(config["COMMON"]["port"])
    if not os.path.exists("web"):
        os.mkdir("web")
except:
    pass

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


#get-запросы

@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})

@app.get("/get_create_table_page")
def get_create_table_page(request:Request):
    return templates.TemplateResponse("create_page_table.html", {"request": request})


#post-запросы

@app.post("/create_table")
def create_table(data=Body()):
    name=data["name"]
    prefix=data["prefix"]
    if(database.create_table(name=name, code_prefix=prefix)):
        return {"message": f"Таблица с именем {name} и префиксом {prefix} успешно создана"}
    else:
        return {"message": f"Ошибка во время создания таблицы"}

uvicorn.run(app, host=host, port=port)