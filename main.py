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

class Device(BaseModel):
    name:str
    prefix:str|None=None
    description:str|None=None
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
    html=html.render()
    return HTMLResponse(html)

@app.get("/table_of_passports")
def get_table_of_passports():
    html=env.get_template("table_of_passports.html")
    data=database.get_all_passports()
    html=html.render(passports=data)
    return HTMLResponse(html)


#post-запросы

@app.post("/create_device")
async def create_device(data=Body()):
    print(data)
    device=data["device"]
    prefix=data["prefix"]
    description=data["description"]
    if not prefix:
        text=database.create_device(device=device,description=description)
    elif not description:
        text=database.create_device(device=device,prefix=prefix)
    else:
        text=database.create_device(device=device,description=description,prefix=prefix)
    return {"message": text}


@app.post("/change_device")
def change_device(data=Body()):
    device=str(data["device"])
    prefix=str(data["prefix"])
    description=str(data["description"])
    if not prefix:
        text=database.change_device(device=device,description=description)
    elif not description:
        text=database.change_device(device=device,prefix=prefix)
    else:
        text=database.change_device(device=device,description=description,prefix=prefix)
    return {"message": text}
    


@app.post("/insert_new_codes_excel")
async def  insert_new_codes(file: UploadFile):
    data=file.file.read()
    html=env.get_template("answer.html")
    text=database.insert_codes_in_bd(data)
    html=html.render(text=text)
    return HTMLResponse(html)



uvicorn.run(app, host=host, port=port)