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
    True-если все успешно
    False-если ошибка
    """
    query_insert_code=f"Insert into passports \
            (name,serial,mac_address,printed)\
            Values (%s,%s,%s,%s)"
    query_check_codes=f"SELECT name,serial,mac_address,printed\
        FROM passports \
        WHERE name=%s and serial=%s and mac_address=%s and printed=%s\
        "
    df=pandas.read_excel(data)
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    for i, row in df.iterrows():
        entry=(str(row[0]),str(row[1]),str(row[2]),row[3])
        cursor.execute(query_check_codes,entry)
        if len(cursor.fetchall())!=0:
            return False
        cursor.execute(query_insert_code,entry)
    conn.commit()
    cursor.close()
    conn.close()
    return True
     


def get_free_codes(count:int):
    """
    Функция для выдачи n-го количества ещё не занятых кодов
    
    из выбранной таблицы и помечает их как выданные(printed=1)
    """
    query_select_codes=f"SELECT name,serial,mac_address\
        FROM passports \
        WHERE printed=0 \
        LIMIT {count}"
    query_mark_gived=f"Update passports \
        SET printed=1\
        WHERE name=%s\
        AND serial=%s\
        AND mac_address=%s"
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cursor=conn.cursor()
    cursor.execute(query_select_codes)
    result_turple=cursor.fetchall()
    if len(result_turple)!=count:
        return False
    for res in result_turple:
        print(res)
        cursor.execute(query_mark_gived,res)
    conn.commit()
    cursor.close()
    conn.close()
    return result_turple

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