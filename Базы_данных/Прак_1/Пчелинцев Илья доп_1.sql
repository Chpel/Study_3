use mydb;

select sum(spj.количество) объём_поставок, sum(spj.количество * p.вес) общий_вес
from spj
	inner join s on s.номер_поставщика = spj.номер_поставщика
    inner join p on p.номер_детали = spj.номер_детали
where
	p.город != 'Афины'
and 
	s.рейтинг >= 10