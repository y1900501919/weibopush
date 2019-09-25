alter table weibos add COLUMN sender TEXT NOT NULL DEFAULT "";
alter table weibos add COLUMN timestamp TEXT NOT NULL DEFAULT 0;
alter table weibos add COLUMN link TEXT NOT NULL DEFAULT "";