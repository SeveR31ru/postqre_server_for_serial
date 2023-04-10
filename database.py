import psycopg2
import json
import configparser
import sys
import re
import os
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


   
def create_table(name:str,code_prefix:str):
    """
    Функция, создающая таблицу по запросу для нового устройства

    Если все хорошо возвращает true, иначе false
    """
    first_string=(name,code_prefix+"_1",0)
    query_create=f"\
        CREATE TABLE {name} \
        (\
        Id SERIAL PRIMARY KEY,\
        device_name CHARACTER VARYING(50),\
        unique_code CHARACTER VARYING(50),\
        printed INTEGER\
        );"
    
    query_insert_first=f"\
        INSERT INTO {name}\
        (device_name,unique_code,printed)\
        VALUES(%s,%s,%s)"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    try:
        cursor.execute(query_create)
    except:
        return False
    cursor.execute(query_insert_first,first_string)
    conn.commit()
    cursor.close()
    conn.close()
    return True  

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
        (device_name,unique_code,printed)\
        VALUES(%s,%s,%s)"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    cursor.execute(query_get_last_row)
    last_row=cursor.fetchone()
    last_row_device=last_row[1]
    last_row_code=last_row[2]
    last_row_code_splitted=last_row_code.split("_")
    last_row_code_prefix=last_row_code_splitted[0]
    last_row_code_number=int(last_row_code_splitted[1])
    for i in range(1,count+1):
        current_code_number=str(last_row_code_number+i)
        target_insert=(name,last_row_code_prefix+"_"+current_code_number,0)
        cursor.execute(query_insert_new_code,target_insert)
    conn.commit()
    cursor.close()
    conn.close()     

def get_free_codes(name:str,count:int):
    """
    Функция для выдачи n-го количества ещё не занятых кодов
    
    из выбранной таблицы и помечает их как выданные(printed=1)
    """
    query_select_codes=f"SELECT id,device_name,unique_code\
        FROM {name} \
        WHERE printed=0 \
        LIMIT {count}"
    query_mark_gived=f"Update {name} \
        SET printed=1\
        WHERE id=%s \
        AND device_name=%s\
        AND unique_code=%s"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    cursor.execute(query_select_codes)
    result_turple=cursor.fetchall()
    if len(result_turple)!=count:
        error=1
        print("В таблице нет столько свободных кодов")
        return error
    for res in result_turple:
        cursor.execute(query_mark_gived,res)
    conn.commit()
    cursor.close()
    conn.close()
    return result_turple


if __name__=="__main__":
    zero=0
