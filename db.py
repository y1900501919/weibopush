import sqlite3
import json

sqlite_file = 'data.db'
conn = sqlite3.connect(sqlite_file)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory


# Creates a weibo in DB if not exists, returns its ID
def create_weibo_if_not_exists(weibo):
    msg_body = weibo['msg_body']
    post_uid = weibo['post_uid']
    weibo_id = weibo['weibo_id']
    img_urls = json.dumps(weibo['img_urls'])
    
    cur = conn.cursor()
    
    query_sql = 'select * from weibos where weibo_id=?'
    cur.execute(query_sql, (weibo_id))
    rows = cur.fetchall()
    if rows: return rows[0]['id']

    insert_sql = 'insert into weibos(msg_body, post_uid, weibo_id, img_urls) values (?,?,?,?)'
    cur.execute(insert_sql, (msg_body, post_uid, weibo_id, img_urls))
    conn.commit()
    return cur.lastrowid