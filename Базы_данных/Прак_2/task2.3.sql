use hdb;
select больничные_палаты.номер_палаты, count(пациенты.рег_номер) as колво_занятых_мест from больничные_палаты
left join пациенты on больничные_палаты.номер_палаты=пациенты.номер_палаты
group by номер_палаты;
