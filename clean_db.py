import sqlite3
import json
from datetime import datetime

sqlite_file = 'data.db'
conn = sqlite3.connect(sqlite_file, check_same_thread=False)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory

def all_weibos():
    cur = conn.cursor()
    query_sql = 'select * from weibos'
    cur.execute(query_sql)
    rows = cur.fetchall()
    return rows

def process_weibo(weibo):
    wid = weibo['id']
    timestamp = weibo['timestamp']
    old_format = '%Y/%m/%d, %a, %H:%M:%S'
    new_format = '%Y-%m-%d %H:%M:%S'
    timestamp = datetime.strptime(timestamp, old_format).strftime(new_format)
    cur = conn.cursor()
    update_sql = 'update weibos set timestamp=? where id=?'
    cur.execute(update_sql, (timestamp, wid,))

    conn.commit()

def run():
    weibos = all_weibos()
    for weibo in weibos:
        process_weibo(weibo)

run()