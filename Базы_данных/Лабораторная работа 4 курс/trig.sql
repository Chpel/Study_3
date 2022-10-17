CREATE TRIGGER insert_trigger
	AFTER INSERT
	ON `zhek`.`tasks`
	FOR EACH ROW INSERT INTO `zhek`.`story_work` (`idЗадача`, `Тип`, `Описание_задачи`, `Заказчик`, `Время_появления`, `Исполнитель`, `Время_завершения`, `Статус`, `инициатор_изменения`, `Время_изменения`)
	VALUES (NEW.`idЗадача`, NEW.`Тип`, NEW.`Описание_задачи`, NEW.`Заказчик`, NEW.`Время_появления`, NEW.`Исполнитель`, NEW.`Время_завершения`, NEW.`Статус`, CURRENT_USER(), NOW());