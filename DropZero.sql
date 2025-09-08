-- DropZero.sql (fixed version)
-- Database schema for DropZero project
-- Secure structure for comments, sentiments, summaries, admins, and users

-- 1. Create database
CREATE DATABASE IF NOT EXISTS DropZero CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE DropZero;

-- 2. Drop tables if they already exist (to reset schema safely)
DROP TABLE IF EXISTS add_comment;
DROP TABLE IF EXISTS summary;
DROP TABLE IF EXISTS sentiment_score;
DROP TABLE IF EXISTS comment;
DROP TABLE IF EXISTS users;    -- changed from 'user' to 'users'
DROP TABLE IF EXISTS admin;

-- 3. Tables

-- i) comment
CREATE TABLE comment (
    comment_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    comment TEXT NOT NULL,
    discussion_topic VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ii) sentiment_score
CREATE TABLE sentiment_score (
    sentiment_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    comment TEXT NOT NULL,
    discussion_topic VARCHAR(255) NOT NULL,
    comment_clean TEXT NOT NULL,
    pos_score DECIMAL(5,4) DEFAULT 0.0,
    neg_score DECIMAL(5,4) DEFAULT 0.0,
    sentiment_score DECIMAL(5,4) DEFAULT 0.0,
    label ENUM("SUPPORT", "NEUTRAL", "CRITICIZE") NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- iii) summary
CREATE TABLE summary (
    discussion_id INT AUTO_INCREMENT PRIMARY KEY,
    discussion_topic VARCHAR(255) NOT NULL,
    type ENUM("SUPPORT","NEUTRAL","CRITICIZE") NOT NULL,
    summary TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- iv) admin
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- v) users (renamed from user)
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- vi) add_comment
CREATE TABLE add_comment (
    discussion_id INT NOT NULL,
    discussion_topic VARCHAR(255) NOT NULL,
    comment TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (discussion_id, user_id, created_at),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;

-- Indexing for better performance
CREATE INDEX idx_discussion_topic ON comment(discussion_topic);
CREATE INDEX idx_sentiment_topic ON sentiment_score(discussion_topic);
CREATE INDEX idx_summary_topic ON summary(discussion_topic);

-- Security best practices:
-- - Store passwords as bcrypt/argon2 hashes in password_hash (never plain text).
-- - Emails are UNIQUE for both users and admins.
-- - Foreign key enforces referential integrity for add_comment.
