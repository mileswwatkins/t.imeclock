DROP TABLE if EXISTS users;
CREATE TABLE users (
    user_id int PRIMARY KEY autoincrement,
    user_name text NOT NULL
);

DROP TABLE if EXISTS proj_spells;
CREATE TABLE proj_spells (
    id int PRIMARY KEY autoincrement,
    user_id text NOT NULL,
    proj_name text NOT NULL,
    start_time text,
    end_time text,
    spell_time int
);
