use `zhek`;
select f.idКвартиры, f.площадь div count(*) as удельная_жилая_площадь from zhek.flats f
 inner join zhek.habitants h on f.idКвартиры = h.квартира
 group by f.idКвартиры
 having удельная_жилая_площадь > 10;
 
 select t.idЗадача,t.время_завершения, описание_задачи from zhek.tasks t
 where t.описание_задачи like 'Покраска%';
 
 
select distinct f.название, t.Описание_задачи from zhek.tasks t
 inner join zhek.workers w on w.idСотрудники = t.Исполнитель
 inner join zhek.brigades b on w.отдел = b.idбригады
 inner join zhek.function f on f.idотрасль = b.отрасль;
 
select w.имя, count(if(Тип = "плановая" and статус = 4, 1, null)) as выполненные_плановые_задачи, count(if(Тип = "внеплановая" and статус = 4, 1, null)) as выполненные_внеплановые_задачи from zhek.tasks t
 right join zhek.workers w on w.idСотрудники = t.Исполнитель
 group by w.idСотрудники;
 
 
 select w.имя from zhek.workers w
 union
 select h.имя from zhek.habitants h;
 
select w.имя, t.idЗадача from zhek.tasks t
 inner join zhek.workers w on w.idСотрудники = t.Исполнитель
 where datediff(t.Время_завершения, t.Время_появления) < 10;

select t.описание_задачи, max(t.время_появления) as дата from zhek.tasks t
 where t.тип = 'плановая'
 group by t.описание_задачи;
 
 
select f.название, count(*) as количество_работников from zhek.workers w
 inner join zhek.brigades b on w.отдел = b.idбригады
 inner join zhek.function f on f.idотрасль = b.отрасль
 group by f.idотрасль;
 
 
select f.название, b.idбригады, count(*) as количество_работников from zhek.workers w
 right join zhek.brigades b on w.отдел = b.idбригады
 inner join zhek.function f on f.idотрасль = b.отрасль
 group by b.idбригады;
 
 
 select f.интернет_компания, count(*) as количество_пользователей from zhek.flats f
 inner join zhek.habitants h on f.idквартиры = h.квартира
 group by f.интернет_компания;
 
 select s.имя, count(t.статус) as количество_задач from zhek.statuses s
 left join zhek.tasks t on t.статус = s.idстатусы
 group by s.idстатусы;
 
select f.idквартиры, count(*) as количество_вызовов from zhek.tasks t
 inner join zhek.habitants h on t.заказчик = h.idЖильцы
 inner join zhek.flats f on f.idквартиры = h.квартира
 where t.тип = 'внеплановая'
 group by f.idквартиры;
 
 
 select f.idКвартиры, f.комнаты, count(*) as количество_жителей from zhek.flats f
 inner join zhek.habitants h on f.idКвартиры = h.квартира
 group by f.idКвартиры
 having count(*) > f.комнаты;
 

 select h.имя from zhek.habitants h
  inner join zhek.flats f on h.квартира = f.idКвартиры
  where f.посл_поверка = (select min(посл_поверка) from zhek.flats);
  

select f.название, count(idЗадача) as количество_задач from zhek.tasks t
 inner join zhek.workers w on w.idСотрудники = t.Исполнитель
 inner join zhek.brigades b on w.отдел = b.idбригады
 right join zhek.function f on f.idотрасль = b.отрасль
 group by f.название;

select f.idКвартиры, f.площадь / f.комнаты as средняя_площадь_комнаты from zhek.flats f
 where f.площадь / f.комнаты = (select max(ff.площадь / ff.комнаты) from zhek.flats ff);

select h.имя, h.квартира from zhek.habitants h
	where h.квартира in (select hh.квартира from zhek.habitants hh
	where hh.имя like '%Сава%');
    

select w.имя, b.idбригады from zhek.workers w
	inner join zhek.brigades b on w.отдел = b.idбригады
	where b.idбригады in (select bb.idбригады from zhek.workers ww
		inner join zhek.brigades bb on ww.отдел = bb.idбригады
		where ww.имя like '%Жданов%');
        
select h.имя from zhek.habitants h
	where h.idЖильцы not in (select distinct t.заказчик from zhek.tasks t
								where t.тип = 'внеплановая');
                                
select w.имя from zhek.workers w
	where w.idСотрудники not in (select distinct t.исполнитель from zhek.tasks t);





 

 
