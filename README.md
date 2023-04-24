# postqre_server_for_serial

Для работы необходимо создать базу с помощью команды Create Database serial_bd.

Первая команда:create table passports(Id Serial PRIMARY KEY,name character varying(30),serial character varying(30) UNIQUE,mac_address character varying(30),printed integer);

Вторая команда:create table prefixes(Id Serial PRIMARY KEY,name character varying(30) UNIQUE,description character varying(30),prefix character varying(30) UNIQUE );
