-- create blog database
-- CREATE DATABASE IF NOT EXISTS myblog 
-- DEFAULT CHARACTER SET utf8 
-- DEFAULT COLLATE utf8_general_ci;

USE myblog;

-- DROP TABLE IF EXISTS blog;
CREATE TABLE IF NOT EXISTS blog (blog_id int(4) primary key NOT NULL, 
	title char(255) NOT NULL, 
	summary text, 
	permalink varchar(512), 
	link varchar(512), 
	status int(4), 
	published int(4), 
	updated int(4), 
	authors int(4), 
	privilege int(4) NOT NULL default 0,
	config text,
	content text, 
	FOREIGN KEY(authors) REFERENCES users(user_id)) ENGINE=MyIsam;

-- DROP TABLE IF EXISTS category;
CREATE TABLE IF NOT EXISTS category (category_id int(4) primary key NOT NULL, 
	name char(255) NOT NULL, 
	description varchar(512)) ENGINE=MyIsam;

-- DROP TABLE IF EXISTS category_link;
CREATE TABLE IF NOT EXISTS category_link(category_link_id int(4) primary key AUTO_INCREMENT,
	category_id int(4) NOT NULL,
	blog_id int(4) NOT NULL,
	FOREIGN KEY(category_id) REFERENCES category(category_id),
	FOREIGN KEY(blog_id) REFERENCES blog(blog_id)) ENGINE=MyIsam;

-- DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users(user_id int(4) primary key NOT NULL AUTO_INCREMENT,
	name varchar(255) NOT NULL,
	passwd varchar(255) NOT NULL,
	localname varchar(255),
	email char(255),
	description varchar(512),
	mobile_phone char(255),
	privilege int(4) NOT NULL default 0) ENGINE=MyIsam;

-- create photo table
CREATE TABLE IF NOT EXISTS photo (createtime int(4) primary key, 
	year int(4) NOT NULL default 1998, 
	month int(4) NOT NULL default 9, 
	name char(255) NOT NULL, 
	image char(255) NOT NULL,
	imagetype int(4), 
	privilege int(4) NOT NULL default 0,
	updated int(4) NOT NULL default 0,
	description varchar(1024)) ENGINE=MyIsam;
CREATE INDEX privilege_ind ON photo (privilege);
CREATE INDEX updated_ind ON photo (updated);
CREATE INDEX year_ind ON photo(year);

-- create sessions
CREATE TABLE IF NOT EXISTS sessions ( 
	session_id CHAR(128) UNIQUE NOT NULL,
	atime timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	data char(255) DEFAULT NULL) ENGINE=MyIsam;

-- create resource table
CREATE TABLE IF NOT EXISTS resources ( 
	resource_id int(4) primary key AUTO_INCREMENT,
	ctime int(4) NOT NULL default 0,
	utime int(4) NOT NULL default 0,
	name char(255) DEFAULT NULL,
	filename char(255) NOT NULL,
	path char(255) DEFAULT NULL,
	md5 char(32) NOT NULL,
	filesize int(4) NOT NULL,
	privilege int(4) NOT NULL default 0,
	description varchar(1024)) ENGINE=MyIsam;

-- create resource category
CREATE TABLE IF NOT EXISTS res_category (category_id int(4) primary key NOT NULL, 
	name char(255) NOT NULL, 
	description varchar(512)) ENGINE=MyIsam;

-- DROP TABLE IF EXISTS res_category_link;
CREATE TABLE IF NOT EXISTS res_category_link(category_link_id int(4) primary key AUTO_INCREMENT,
	category_id int(4) NOT NULL,
	resource_id int(4) NOT NULL,
	FOREIGN KEY(category_id) REFERENCES res_category(category_id),
	FOREIGN KEY(resource_id) REFERENCES resources(resource_id)) ENGINE=MyIsam;

-- ALTER TABLE users CHANGE user_id user_id INT(4) NOT NULL AUTO_INCREMENT;
