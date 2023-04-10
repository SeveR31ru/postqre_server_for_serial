from fastapi import FastAPI, Request, Body,HTTPException,UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import configparser
import os

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



uvicorn.run(app, host=host, port=port)