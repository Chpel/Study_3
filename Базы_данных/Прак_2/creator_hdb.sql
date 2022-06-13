create schema hdb;
use hdb;

create table больничные_палаты 
(
номер_палаты numeric(3,0) not null primary key,
количество_коек numeric(3,0) not null,
отделение char(20) charset utf8 not null 
);

create table врачи
(
идентификатор numeric(6,0) not null primary key,
фио char(20) charset utf8 not null,
отделение char(20) charset utf8 not null,
специализация char(20) charset utf8 not null
);

create table пациенты
(
рег_номер numeric(6,0) not null primary key,
фио char(20) charset utf8 not null,
пол char default 'Ж' not null,
номер_полиса char(15) charset utf8 not null,
дата_поступления date not null,
номер_палаты numeric(3,0) not null,
лечащий_врач numeric(6,0) not null,
диагноз char(20) charset utf8,
дата_выписки date null,
constraint пациенты_палаты_номер_fk
        foreign key (номер_палаты) references больничные_палаты (номер_палаты),
constraint пациенты_врачи_номер_fk
        foreign key (лечащий_врач) references врачи (идентификатор)
);