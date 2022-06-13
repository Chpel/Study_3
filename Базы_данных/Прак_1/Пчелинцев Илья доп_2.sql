select distinct j.название
from spj
	inner join p on p.номер_детали = spj.номер_детали
    inner join j on j.номер_изделия = spj.номер_изделия
where exists (select *
	from spj spj1
		inner join p p1 on p1.номер_детали = spj1.номер_детали
		inner join j j1 on j1.номер_изделия = spj1.номер_изделия
	where 
		j1.номер_изделия = spj.номер_изделия
	and 
		p1.город = j1.город)