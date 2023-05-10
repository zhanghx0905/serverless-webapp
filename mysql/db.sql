DROP DATABASE IF EXISTS aws_test;
CREATE DATABASE aws_test;

USE aws_test;

CREATE TABLE Task (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    dueDate DATE NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upload TINYINT(1) DEFAULT 0,
    labels VARCHAR(255) DEFAULT ""
);

CREATE TABLE User (
    username VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255) NOT NULL,
    token VARCHAR(255)
);

INSERT INTO Task (title, body, dueDate)
VALUES
    ('Task 1', 'Body of Task 1', '2023-05-15'),
    ('Task 2', 'Body of Task 2', '2023-05-20');

INSERT INTO User (username, password)
VALUES ('test', '123456');
