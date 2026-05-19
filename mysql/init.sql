CREATE DATABASE IF NOT EXISTS eshop;
USE eshop;
CREATE TABLE IF NOT EXISTS users (
   	id INT AUTO_INCREMENT PRIMARY KEY,
   	name VARCHAR(16) NOT NULL,
   	password VARCHAR(64) NOT NULL,
   	tel VARCHAR(20),
   	roles VARCHAR(16) DEFAULT 'consumer' 
);
CREATE TABLE IF NOT EXISTS goods (
   	id INT AUTO_INCREMENT PRIMARY KEY,
   	merchant_id INT NOT NULL,
  	name VARCHAR(100) NOT NULL,
   	description TEXT,
   	price DECIMAL(10,2) NOT NULL,
   	category VARCHAR(50),
   	image_url VARCHAR(255),
  	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS cart (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  user_id     INT NOT NULL,
  goods_id    INT NOT NULL,
  quantity    INT NOT NULL DEFAULT 1,
  created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_cart_item (user_id, goods_id)  -- 同一商品不重复，只加数量
);
