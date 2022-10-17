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
 
 
 
 
select w.имя, t.idЗадача from zhek.tasks t
 inner join zhek.workers w on w.idСотрудники = t.Исполнитель
 where datediff(t.Время_завершения, t.Время_появления) < 10;

 
 
select * from zhek.tasks t
  right join zhek.workers w on w.idСотрудники = t.исполнитель;