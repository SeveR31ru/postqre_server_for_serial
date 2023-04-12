from fastapi import FastAPI, Request, Body,HTTPException,UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
import uvicorn
import configparser
import os
import database
import pandas

try:
    # получение конфигов
    config = configparser.ConfigParser()
    config.read("./settings.ini")
    host = str(config["COMMON"]["host"])
    port = int(config["COMMON"]["port"])
except:
    pass

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
env=Environment(loader=FileSystemLoader('templates'))



#get-запросы

@app.get("/")
def main_page():
    html=env.get_template("main.html")
    html=html.render()
    return HTMLResponse(html)
@app.get("/insert_new_codes_page")
def insert_page():
    html=env.get_template("insert_codes_page.html")
    html=html.render()
    return HTMLResponse(html)

@app.get("/get_free_codes_page")
def get_page():
    html=env.get_template("get_codes_page.html")
    html=html.render()
    return HTMLResponse(html)

@app.get("/table_of_passports")
def get_table_of_passports():
    html=env.get_template("table_of_passports.html")
    data=database.get_all_passports()
    html=html.render(passports=data)
    return HTMLResponse(html)



#post-запросы


@app.post("/insert_new_codes_excel")
async def  insert_new_codes(file: UploadFile):
    data=file.file.read()
    html=env.get_template("answer.html")
    if(database.insert_codes_in_bd(data)):
        text="Паспорта успешно добавлены в таблицу"
    else:
        text="Ошибка во время добавления паспортов. Возможно, вы пытаетесь добавить уже имеющиеся паспорта\
        ,к базе нет подключения сейчас или случилась иная непредвиденная ошибка"
    html=html.render(text=text)
    return HTMLResponse(html)


@app.post("/give_free_codes_excel")
def give_free_codes_excel(count:int):
    data=database.get_free_codes(count)
    result = pandas.DataFrame(data, columns=['Наименование'	,'Серийный номер','MAC-адрес'])
    output=result.to_excel(f"Свободные_коды_в_количестве_{count}.xlsx",index=False,)
    return FileResponse(path=f"Свободные_коды_в_количестве_{count}.xlsx", media_type='application/octet-stream', filename=f"Свободные_коды_в_количестве_{count}.xlsx")



uvicorn.run(app, host=host, port=port)