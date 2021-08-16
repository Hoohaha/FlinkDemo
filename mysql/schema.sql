create database if not exists `demo` default character set utf8 collate utf8_general_ci;

use demo;

DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
  `id` bigint(20) NOT NULL,
  `created_at` bigint(40) DEFAULT NULL,
  `last_modified` bigint(40) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `first_name` varchar(255) DEFAULT NULL,
  `last_name` varchar(255) DEFAULT NULL,
  `username` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `user` (`id`, `created_at`, `last_modified`, `email`, `first_name`, `last_name`, `username`)
VALUES
    (0,1490257904,1490257904,'john.doe@example.com','John','Doe','user');



CREATE TABLE `keyErrorLog` (
  `task_id` bigint(40) DEFAULT NULL,
  `task_hash` bigint(40) DEFAULT NULL,
  `log_type` varchar(255) DEFAULT "",
  `rate` float,
  `message` TEXT DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `Task` (
  `task_id` bigint(40) DEFAULT NULL,
  `testcase` varchar(255) DEFAULT NULL,
  `platform` varchar(255) DEFAULT "",
  `compiler` varchar(255) DEFAULT "",
  `target` varchar(255) DEFAULT "",
  `category` varchar(255) DEFAULT NULL,
  `issue` varchar(120) DEFAULT NULL,
  `buildresult` varchar(255) DEFAULT NULL,
  `buildstart` TIMESTAMP(3) DEFAULT NULL,
  `buildduration` TIME(3) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


LOAD DATA LOCAL INFILE '/opt/55682-data.csv' INTO TABLE Task FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;
LOAD DATA LOCAL INFILE '/opt/197812-data.csv' INTO TABLE Task FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES;
