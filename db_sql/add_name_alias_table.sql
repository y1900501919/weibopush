CREATE TABLE "name_alias" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"name"	TEXT NOT NULL,
	"alias"	TEXT NOT NULL UNIQUE
);