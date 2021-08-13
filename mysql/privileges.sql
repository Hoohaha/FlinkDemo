use mysql;
select host, user from user;
create user 'test'@'%' IDENTIFIED WITH mysql_native_password by '123456';
GRANT ALL PRIVILEGES on *.* to 'test'@'%';

FLUSH PRIVILEGES;
