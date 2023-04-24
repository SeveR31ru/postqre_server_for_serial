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
     


def create_template(template:str,description:str=None,prefix:str=None):
    """
    Функция создания нового шаблона. Первое созданное новое устройство будет вставлено в таблицу автоматически
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
    data=[template]
    cursor.execute(query_check_device,data)
    if len(cursor.fetchall())!=0:
            return "Девайс с таким именем уже имеется. Отмена операции"
    data=[prefix]
    cursor.execute(query_check_prefix,data)
    if len(cursor.fetchall())!=0:
            return "Девайс с таким префиксом уже имеется. Отмена операции"
    
    if prefix is None:
        selected_query=query_create_device_description
        data=[template,description]
    elif description is None:
        selected_query=query_create_device_prefix
        data=[template,prefix]
    else:
        selected_query=query_create_device_full
        data=[template,description,prefix]
    
    try:
        cursor.execute(selected_query,data)
    except:
        return "Непредвиденная ошибка во время создания записи в таблице префиксов, отмена операции"
    
    try:
        code_data=[template,prefix+"_1",'0']
        cursor.execute(query_create_first_code,code_data)
    except:
        return "Непредвиденная ошибка при создании первого кода, отмена операции"
    conn.commit()
    cursor.close()
    conn.close()
    return f"Устройство с именем:{template} \n \
        префиксом:{prefix}\n \
        описанием:{description} \n \
        успешно создано и первый код сгенерирован"





def change_template(template:str,prefix:str=None,description:str=None):
    """
    Функция изменения описания и префикса имеющегося девайса
    аргументы:
    template- название шаблона 
    prefix-желаемый префикс
    description-желаемое описание
    @return:
    str-строка ошибки либо строка успеха операции
    """
    query_change_template_full=f"Update prefixes \
        SET prefix=%s,description=%s where name=%s"
    query_change_template_prefix=f"Update prefixes \
        SET prefix=%s where name=%s"
    query_change_template_description=f"Update prefixes \
        SET description=%s where name=%s"
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor=conn.cursor()
    except:
        return "Не удалось подключиться к базе"
    if prefix is None:
        query=query_change_template_description
        data=(description,template)
    elif description is None:
        query=query_change_template_prefix
        data=(prefix,template)
    else:
        query=query_change_template_full
        data=(prefix,description,template)
    try:
        cursor.execute(query,data)
    except:
        return "Непредвиденная ошибка во время изменения, отмена операции. Вероятнее всего было найдено неуникальное значение в столбце имен или префиксов"
    conn.commit()
    cursor.close()
    conn.close()
    return f"Шаблон с именем:{template} успешно изменен \n \
        Префикс изменен на:{prefix}\
        Описание изменено на:{description}"

     
def generate_free_codes(template:str,count:int):
    """
   Функция, которая генерирует n-ое количество новых кодов для выбранного шаблона
   аргументы:
   @template- имя выбранного шаблона
   @count-количество необходимых кодов
   return:
   строка о выполнении или невыполнении операции

    """
    query_get_last_row=f"SELECT * \
    FROM passports WHERE name=%s \
        ORDER BY id DESC \
        LIMIT 1;"
    query_insert_new_code=f"\
        INSERT INTO passports\
        (name,serial,printed)\
        VALUES(%s,%s,%s)"
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor=conn.cursor()
    except:
        return "Не удалось подключиться к базе"
    try:
        cursor.execute(query_get_last_row,(template,))
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
            target_insert=(template,last_row_code_prefix+"_"+current_code_number,0)
            cursor.execute(query_insert_new_code,target_insert)
    except:
        return "Ошибка во время вставки новых кодов"
    conn.commit()
    cursor.close()
    conn.close()     
    return f"Для шаблона устройства {template} успешно создано {count} кодов"

def get_all_passports():
    """
    Функция, которая всю таблицу паспортов кортежем из строк
    """
    query_get_all_passports=f"SELECT * FROM passports"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    cursor.execute(query_get_all_passports)
    data=cursor.fetchall()
    return data

def get_all_templates_names():
    """
    Функция,возвращающая все имена шаблонов устройств
    
    """
    query_get_names=f"SELECT name FROM prefixes"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    cursor.execute(query_get_names)
    data=cursor.fetchall()
    result=[]
    for row in data:
        result.append(row[0])
    return result





