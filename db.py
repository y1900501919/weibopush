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


# Creates a weibo in DB if not exists, returns exist status and its ID
def create_weibo_if_not_exists(weibo):
    msg_body = weibo['msg_body']
    post_uid = weibo['post_uid']
    weibo_id = weibo['weibo_id']
    img_urls = json.dumps(weibo['img_urls'])
    
    cur = conn.cursor()
    
    query_sql = 'select * from weibos where weibo_id=?'
    cur.execute(query_sql, (weibo_id,))
    rows = cur.fetchall()
    if rows: return True, rows[0]['id']

    insert_sql = 'insert into weibos(msg_body, post_uid, weibo_id, img_urls) values (?,?,?,?)'
    cur.execute(insert_sql, (msg_body, post_uid, weibo_id, img_urls,))
    conn.commit()
    return False, cur.lastrowid


def get_weibo_with_wid(wid):
    cur = conn.cursor()

    query_sql = 'select * from weibos where id=?'
    cur.execute(query_sql, (wid,))
    rows = cur.fetchall()
    if rows: return rows[0]
    return None


def get_weibo_feedback(wid, sender):
    cur = conn.cursor()

    query_sql = 'select * from weibo_feedbacks where wid=? and feedback_user_id=?'
    cur.execute(query_sql, (wid, sender,))
    rows = cur.fetchall()
    if rows: return rows[0]
    return None


def get_random_weibo():
    cur = conn.cursor()
    query_sql = 'select * FROM weibos order by RANDOM() limit 1'
    cur.execute(query_sql)
    rows = cur.fetchall()
    if rows: return rows[0]
    return None


def update_weibo_feedback(wid, rating, sender_puid):
    cur = conn.cursor()
    update_sql = 'update weibo_feedbacks set rating=? where wid=? and feedback_user_id=?'
    cur.execute(update_sql, (rating, wid, sender_puid,))

    conn.commit()


def save_weibo_feedback(wid, rating, sender_puid):
    cur = conn.cursor()
    update_sql = 'insert into weibo_feedbacks(wid, rating, feedback_user_id) values (?,?,?)'
    cur.execute(update_sql, (wid, rating, sender_puid,))

    conn.commit()

def get_all_ratings(wid):
    cur = conn.cursor()

    query_sql = 'select * from weibo_feedbacks where wid=?'
    cur.execute(query_sql, (wid,))
    rows = cur.fetchall()
    return rows
