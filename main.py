from fastapi import FastAPI, Request, Body,HTTPException,UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader
from pydantic import BaseModel
import uvicorn
import configparser
import os
import database
import pandas
import json


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


#запросы по открытию страниц меню
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

@app.get("/generate_free_codes_page")
def get_page():
    html=env.get_template("generate_free_codes_page.html")
    templates_list=database.get_all_templates_names()
    html=html.render(templates_list=templates_list)
    return HTMLResponse(html)

@app.get("/table_of_passports")
def get_table_of_passports():
    html=env.get_template("table_of_passports.html")
    data=database.get_all_passports()
    html=html.render(passports=data)
    return HTMLResponse(html)


#post-запросы

@app.post("/create_template")
async def create_template(data=Body()):
    template=data["template"]
    prefix=data["prefix"]
    description=data["description"]
    if not template:
        return {"message":"Введите имя шаблона"}  
    if template and not prefix:
        return {"message": "Введите префикс"}
    if not prefix:
        text=database.create_template(template=template,description=description)
    elif not description:
        text=database.create_template(template=template,prefix=prefix)
    else:
        text=database.create_template(template=template,description=description,prefix=prefix)
    return {"message": text}


@app.post("/change_template")
async def change_template(data=Body()):
    template=data["template"]
    prefix=data["prefix"]
    description=data["description"]
    if not template:
        return {"message":"Введите имя шаблона"}
    if not prefix and not description:
        return {"message":"Введите хотя бы один параметр для изменения"}
    if not prefix:
        text=database.change_template(template=template,description=description)
    elif not description:
        text=database.change_template(template=template,prefix=prefix)
    else:
        text=database.change_template(template=template,description=description,prefix=prefix)
    return {"message": text}

@app.post("/generate_codes")
async def generate_codes(data=Body()):
    template=str(data["template"])
    count=data["count"]
    if not template:
        return {"message":"Введите имя шаблона"}
    if not count:
        return {"message":"Введите количество кодов"}
    text=database.generate_free_codes(template, int(count))
    return  {"message": text}
    


@app.post("/insert_new_codes_excel")
async def  insert_new_codes(file: UploadFile):
    data=file.file.read()
    html=env.get_template("answer.html")
    text=database.insert_codes_in_bd(data)
    html=html.render(text=text)
    return HTMLResponse(html)



uvicorn.run(app, host=host, port=port)