USE `zhek` ;

CREATE ROLE `диспетчер`;
GRANT INSERT, DELETE, SELECT, ALTER ON TABLE `задачи` TO `диспетчер`;
CREATE USER `МарьИванна` IDENTIFIED BY '123';
GRANT `диспетчер` TO `МарьИванна`;
set default role `диспетчер` to `МарьИванна`;
FLUSH PRIVILEGES;

USE `zhek` ;
CREATE ROLE `диспетчер`;
GRANT INSERT, DELETE, SELECT, ALTER ON TABLE `задачи` TO `диспетчер`;
CREATE USER 'root2' IDENTIFIED BY '123';
GRANT `диспетчер` TO `root2`;
set default role `диспетчер` to `root2`;
FLUSH PRIVILEGES;

CREATE ROLE `бригадир`;
GRANT SELECT (`Исполнитель`), ALTER ON TABLE `задачи` TO `бригадир`;
GRANT SELECT (`статус`), ALTER ON TABLE `задачи` TO `бригадир`;
CREATE USER 'ФёдорПалыч';
GRANT `бригадир` TO `ФёдорПалыч`;

CREATE ROLE `сотрудник`;
GRANT SELECT (`статус`), ALTER ON TABLE `задачи` TO `сотрудник`;
CREATE USER 'МихаилПетрович';
GRANT `сотрудник` TO `МихаилПетрович`;

CREATE ROLE `проживающий`;
GRANT SELECT, INSERT ON TABLE `задачи` TO `проживающий`;
GRANT SELECT (`статус`), ALTER ON TABLE `задачи` TO `проживающий`;
CREATE USER 'РаиссаСтепанна';
GRANT `проживающий` TO `РаиссаСтепанна`;

CREATE ROLE `староста`;
GRANT SELECT, INSERT, DELETE ON TABLE `жильцы` TO `староста`;
CREATE USER 'ИзольдаТихоновна';
GRANT `староста` TO `ИзольдаТихоновна`;