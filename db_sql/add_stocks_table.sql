CREATE TABLE "stockholder" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"puid"	TEXT NOT NULL UNIQUE,
	"money"	INTEGER NOT NULL DEFAULT 1000
);
CREATE TABLE "stocks" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"puid"	INTEGER NOT NULL,
	"stock_name"	TEXT NOT NULL,
	"count"	INTEGER NOT NULL DEFAULT 0
);