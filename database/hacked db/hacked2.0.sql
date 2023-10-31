BEGIN TRANSACTION;
CREATE TABLE likedMeals (
        id INTEGER PRIMARY KEY,
        username TEXT,
        likedMeals TEXT
    );
INSERT INTO "likedMeals" VALUES(1,'admin','52894');
INSERT INTO "likedMeals" VALUES(2,'admin','op');
CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    );
INSERT INTO "users" VALUES(1,'admin','1234');
COMMIT;
