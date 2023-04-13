import psycopg2
import json
import configparser
import sys
import re
import os
import pandas
"""
printed:
0- Созданы, не выданы
1- Выданы, но ещё не распечатаны
2- Распечатаны и подтверждены

"""


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


def insert_codes_in_bd(data:bytes):
    """
    функция для вставки новых паспортов в базу

    @аргументы:
    data-байты, полученные из эксель файла для дальнейшего перевода в нормальный вид и загрузку в бд
    return:
    str-письменный ответ на запрос
    """
    query_insert_code=f"Insert into passports \
            (name,serial,mac_address,printed)\
            Values (%s,%s,%s,%s)"
    query_check_codes=f"SELECT name,serial,mac_address,printed\
        FROM passports \
        WHERE name=%s and serial=%s and mac_address=%s and printed=%s\
        "
    try:
        df=pandas.read_excel(data)
    except:
        return "Ошибка чтения таблицы"
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor=conn.cursor()
    except:
        return "Не удалось подключиться к базе"
    for i, row in df.iterrows():
        entry=(str(row[0]),str(row[1]),str(row[2]),row[3])
        cursor.execute(query_check_codes,entry)
        if len(cursor.fetchall())!=0:
            return "Обнаружена коллизия кодов. Код из введенной таблицы уже имеется в таблице. Отмена операции"
        cursor.execute(query_insert_code,entry)
    conn.commit()
    cursor.close()
    conn.close()
    return "Паспорта успешно добавлены в таблицу"
     


def create_device(device:str,description:str=None,prefix:str=None):
    """
    Функция создания нового девайса. Первое созданное новое устройство будет вставлено в таблицу автоматически
    device-название девайса
    description- описание
    prefix-префикс
    str-строка ошибки либо строка успеха операции
    """
    query_create_device_full=f"Insert into prefixes  \
            (name,description,prefix)\
            Values (%s,%s,%s)"
    query_create_device_prefix=f"Insert into prefixes  \
            (name,description,prefix)\
            Values (%s,%s,%s)"
    query_create_device_description=f"Insert into prefixes  \
            (name,description,prefix)\
            Values (%s,%s,%s)"
    query_create_first_code=f"Insert into passports  \
            (name,serial,printed)\
            Values (%s,%s,%s)"
    query_check_device=f"SELECT name\
        FROM prefixes \
        WHERE name=%s \
            "
    query_check_prefix=f"SELECT prefix\
        FROM prefixes \
        WHERE prefix=%s \
            "

    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor=conn.cursor()
    except:
        return "Не удалось подключиться к базе"
    data=[device]
    cursor.execute(query_check_device,data)
    if len(cursor.fetchall())!=0:
            return "Девайс с таким именем уже имеется. Отмена операции"
    data=[prefix]
    cursor.execute(query_check_prefix,data)
    if len(cursor.fetchall())!=0:
            return "Девайс с таким префиксом уже имеется. Отмена операции"
    
    if prefix is None:
        selected_query=query_create_device_description
        data=[device,description]
    elif description is None:
        selected_query=query_create_device_prefix
        data=[device,prefix]
    else:
        selected_query=query_create_device_full
        data=[device,description,prefix]
    
    try:
        cursor.execute(selected_query,data)
    except:
        return "Непредвиденная ошибка во время создания записи в таблице префиксов, отмена операции"
    
    try:
        code_data=[device,prefix+"_1",'0']
        cursor.execute(query_create_first_code,code_data)
    except:
        return "Непредвиденная ошибка при создании первого кода, отмена операции"
    conn.commit()
    cursor.close()
    conn.close()
    return f"Устройство с именем {device} \n \
        префиксом : {prefix}\n \
        описанием: {description} \n \
        успешно создано и первый код сгенерирован"





def change_device(device:str,prefix:str=None,description:str=None):
    """
    Функция изменения описания и префикса имеющегося девайса
    аргументы:
    device-название девайса
    prefix-желаемый префикс
    description-желаемое описание
    @return:
    str-строка ошибки либо строка успеха операции
    """
    query_change_device_full=f"Insert into prefixes  \
            (name,description,prefix)\
            Values (%s,%s,%s)"
    query_change_device_prefix=f"Insert into prefixes  \
            (name,description,prefix)\
            Values (%s,%s,%s)"
    query_change_device_description=f"Insert into prefixes  \
            (name,description,prefix)\
            Values (%s,%s,%s)"
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor=conn.cursor()
    except:
        return "Не удалось подключиться к базе"
    if prefix is None:
        query=query_change_device_description
        data=(name,description)
    elif description is None:
        query=query_change_device_prefix
        data=(name,prefix)
    else:
        query=query_change_device_full
        data=(name,prefix,description)
    try:
        cursor.execute(query,data)
    except:
        return "Непредвиденная ошибка во время изменения, отмена операции"
    conn.commit()
    cursor.close()
    conn.close()
    return f"Девайс с именем {name} успешно изменен /n \
        Префикс изменен на: {prefix}\
        Описание изменено на: {description}"

     
def generate_free_codes(name:str,count:int):
    """
    Функция, добавляющая n-е количество незанятых кодов
    в БД в выбранную таблицу(printed=0)
    """
    query_get_last_row=f"SELECT * \
    FROM {name} \
        ORDER BY id DESC, \
        id DESC \
        LIMIT 1;"
    query_insert_new_code=f"\
        INSERT INTO {name}\
        (name,serial,printed)\
        VALUES(%s,%s,%s)"
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor=conn.cursor()
    except:
        return "Не удалось подключиться к базе"
    try:
        cursor.execute(query_get_last_row)
    except:
        return "Не удалось получить последний имеющийся код устройства"    
    last_row=cursor.fetchone()
    last_row_device=last_row[1]
    last_row_code=last_row[2]
    last_row_code_splitted=last_row_code.split("_")
    last_row_code_prefix=last_row_code_splitted[0]
    last_row_code_number=int(last_row_code_splitted[1])
    try:
        for i in range(1,count+1):
            current_code_number=str(last_row_code_number+i)
            target_insert=(name,last_row_code_prefix+"_"+current_code_number,0)
            cursor.execute(query_insert_new_code,target_insert)
    except:
        return "Ошибка во время вставки новых кодов"
    conn.commit()
    cursor.close()
    conn.close()     
    return f"Для устройства {name} успешно создано {count} кодов"

def get_all_passports():
    """
    Функция, которая всю таблицу паспортов кортежем из строк
    """
    query_get_all_codes=f"SELECT * FROM passports"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    cursor.execute(query_get_all_codes)
    data=cursor.fetchall()
    return data
