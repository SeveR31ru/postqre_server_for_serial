import psycopg2
import json
import configparser


try:
    # получение конфигов
    config = configparser.ConfigParser()
    config.read("./settings.ini")
    host = str(config["DB"]["host"])
    port = int(config["DB"]["port"])
    user=str(config["DB"]["user"])
    password=str(config["DB"]["password"])
    dbname=str(config["DB"]["dbname"])
except:
    pass
    










conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
if conn:
    print("Подключение установлено")
else:
    print("Error")
conn.close()