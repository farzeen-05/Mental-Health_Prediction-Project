CREATE TABLE `users` (
    `u_id` INT(11) NOT NULL AUTO_INCREMENT,
    `u_name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password` VARCHAR(255) NOT NULL,
    PRIMARY KEY(`u_id`)
)