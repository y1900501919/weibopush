PRAGMA foreign_keys=off;

BEGIN TRANSACTION;

ALTER TABLE weibo_feedbacks RENAME TO _weibo_feedbacks_old;

CREATE TABLE "weibo_feedbacks" (
	"id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
	"wid"	INTEGER NOT NULL,
	"feedback_user_id"	TEXT NOT NULL,
	"rating"	INTEGER DEFAULT 0,
	"emo"	TEXT DEFAULT ""
);

INSERT INTO weibo_feedbacks (id, wid, feedback_user_id, rating, emo)
  SELECT id, wid, feedback_user_id, rating, emo
  FROM _weibo_feedbacks_old;

COMMIT;

PRAGMA foreign_keys=on;