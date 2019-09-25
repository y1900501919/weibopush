import sqlite3
import json

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
    body = weibo['msg_body']
    wid = weibo['id']
    body_lines = body.split('\n')
    timestamp = body_lines[0]
    sender = body_lines[1]
    link = body_lines[-1]
    msg_body = '\n'.join(body_lines[2:-1])
    cur = conn.cursor()
    update_sql = 'update weibos set timestamp=?, sender=?, link=?, msg_body=? where id=?'
    cur.execute(update_sql, (timestamp, sender, link, msg_body, wid,))

    conn.commit()

def run():
    weibos = all_weibos()
    for weibo in weibos:
        process_weibo(weibo)

run()