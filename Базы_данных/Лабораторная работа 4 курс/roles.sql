USE `zhek` ;

CREATE ROLE `диспетчер`;
GRANT INSERT, DELETE, SELECT, UPDATE ON TABLE `tasks` TO `диспетчер`;
CREATE USER `МарьИванна` IDENTIFIED BY '123';
GRANT `диспетчер` TO `МарьИванна`;
set default role `диспетчер` to `МарьИванна`;
FLUSH PRIVILEGES;

CREATE ROLE `бригадир`;
GRANT SELECT (`idЗадача`, `Описание_задачи`, `Исполнитель`, `Статус`), UPDATE (`Исполнитель`) ON TABLE `tasks` TO `бригадир`;
CREATE USER 'ФёдорПалыч' IDENTIFIED BY '123';
GRANT `бригадир` TO `ФёдорПалыч`;
set default role `бригадир` to `ФёдорПалыч`;
FLUSH PRIVILEGES;

CREATE ROLE `сотрудник`;
GRANT SELECT (`idЗадача`, `Описание_задачи`, `Заказчик`, `статус`), UPDATE (`статус`) ON TABLE `tasks` TO `сотрудник`;
CREATE USER 'МихаилПетрович' IDENTIFIED BY '123';
GRANT `сотрудник` TO `МихаилПетрович`;
set default role `сотрудник` to `МихаилПетрович`;
FLUSH PRIVILEGES;

CREATE ROLE `проживающий`;
GRANT SELECT (`idЗадача`, `Описание_задачи`, `Заказчик`, `статус`), 
	  INSERT (`idЗадача`, `Описание_задачи`, `Заказчик`, `статус`), UPDATE (`статус`) ON TABLE `tasks` TO `проживающий`;
GRANT SELECT, UPDATE (`интернет_компания`) ON TABLE `flats` TO `проживающий`;
CREATE USER 'РаиссаСтепанна' IDENTIFIED BY '123';
GRANT `проживающий` TO `РаиссаСтепанна`;
set default role `проживающий` to `РаиссаСтепанна`;
FLUSH PRIVILEGES;

CREATE ROLE `староста`;
GRANT SELECT, INSERT, DELETE ON TABLE `habitants` TO `староста`;
GRANT SELECT, UPDATE (`посл_поверка`) ON TABLE `flats` TO `староста`;
CREATE USER 'ИзольдаТихоновна';
GRANT `староста` TO `ИзольдаТихоновна`;
set default role `староста` to `ИзольдаТихоновна`;
FLUSH PRIVILEGES;