# postqre_server_for_serial

Для работы необходимо создать базу с помощью команды Create Database serial_bd.

После этого исполнить в ней команду create table passports(Id Serial PRIMARY KEY,name character varying(30),serial character varying(30),mac_address character varying(30),printed integer);