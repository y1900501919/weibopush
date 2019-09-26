import sqlite3
import json
from utils import date_to_str

sqlite_file = 'data.db'
conn = sqlite3.connect(sqlite_file, check_same_thread=False)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

conn.row_factory = dict_factory


def dbget(query, params=tuple()):
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    return rows


def dbinsert(query, params):
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()
    return cur.lastrowid

def dbupdate(query, params):
    cur = conn.cursor()
    cur.execute(query, params)
    conn.commit()

# Creates a weibo in DB if not exists, returns exist status and its ID
def create_weibo_if_not_exists(weibo):
    msg_body = weibo['msg_body']
    post_uid = weibo['post_uid']
    weibo_id = weibo['weibo_id']
    sender = weibo['sender']
    link = weibo['link']
    timestamp = weibo['timestamp']
    img_urls = json.dumps(weibo['img_urls'])
    
    rows = dbget('select * from weibos where weibo_id=?', (weibo_id,))
    if rows: return True, rows[0]['id']

    insert_sql = 'insert into weibos(msg_body, timestamp, sender, link, post_uid, weibo_id, img_urls) values (?,?,?,?,?,?,?)'
    lastrowid = dbinsert(insert_sql, (msg_body, timestamp, sender, link, post_uid, weibo_id, img_urls,))
    return False, lastrowid


def get_weibo_with_wid(wid):
    rows = dbget('select * from weibos where id=? and deleted=0', (wid,))
    if rows: return rows[0]
    return None


def check_symbol_is_poster(symbol):
    rows = dbget('SELECT sender FROM weibos WHERE sender=?', (symbol,))
    return True if rows else False

def check_alias_exists(alias):
    rows = dbget('SELECT alias FROM name_alias WHERE alias=?', (alias,))
    return True if rows else False

def save_alias(alias, name):
    dbinsert('insert into name_alias(name, alias) values (?,?)', (name, alias,))
    
def unalias(alias):
    unaliased_name = get_name_from_alias(alias)
    return unaliased_name if unaliased_name else alias

def get_name_from_alias(alias):
    rows = dbget('SELECT name FROM name_alias WHERE alias=?', (alias,))
    if rows:
        return rows[0]['name']
    return None


def get_weibos_with_poster_after_date(poster_name, date_start):
    query_sql = '''
        SELECT COUNT(id) n, date(timestamp) day
        FROM weibos
        WHERE sender=? and 
        timestamp > ?
        GROUP BY date(timestamp);
    '''
    rows = dbget(query_sql, (poster_name, date_start,))
    return rows


def get_weibo_feedback(wid, sender):
    rows = dbget('select * from weibo_feedbacks where wid=? and feedback_user_id=?', (wid, sender,))
    if rows: return rows[0]
    return None


def get_random_weibo():
    rows = dbget('select * FROM weibos where deleted=0 order by RANDOM() limit 1')
    if rows: return rows[0]
    return None

def delete_weibo(wid):
    dbupdate('update weibos set deleted=1 where id=?', (wid,))

def recover_weibo(wid):
    dbupdate('update weibos set deleted=0 where id=?', (wid,))

def search_weibo(keywords):
    append_sql = ['msg_body like "%{}%"'.format(keyword) for keyword in keywords]
    query_sql = 'select * from weibos where ' + ' or '.join(append_sql) + ' and deleted=0'
    rows = dbget(query_sql)
    return rows

def update_weibo_feedback_rating(wid, rating, sender_puid):
    dbupdate('update weibo_feedbacks set rating=? where wid=? and feedback_user_id=?', (rating, wid, sender_puid,))


def update_weibo_feedback_emo(wid, emo, sender_puid):
    dbupdate('update weibo_feedbacks set emo=? where wid=? and feedback_user_id=?', (emo, wid, sender_puid,))


def save_weibo_feedback_rating(wid, rating, sender_puid):
    dbinsert('insert into weibo_feedbacks(wid, rating, feedback_user_id) values (?,?,?)', (wid, rating, sender_puid,))


def save_weibo_feedback_emo(wid, emo, sender_puid):
    dbinsert('insert into weibo_feedbacks(wid, emo, feedback_user_id) values (?,?,?)', (wid, emo, sender_puid,))


def get_all_ratings(wid):
    rows = dbget('select * from weibo_feedbacks where wid=?', (wid,))
    return rows

def get_all_senders():
    rows = dbget('select distinct sender from weibos')
    return [x['sender'] for x in rows]

def create_stockholder(puid):
    dbinsert('insert into stockholder(puid) values (?)', (puid,))

def get_stockholder(puid):
    rows = dbget('select * from stockholder where puid=?', (puid,))
    return rows[0] if rows else None

def update_stockholder(puid, money):
    dbupdate('update stockholder set money=? where puid=?', (money, puid,))

def get_holder_stocks(puid):
    rows = dbget('select * from stocks where puid=?', (puid,))
    return rows

def get_holder_stock(puid, stock_name):
    rows = dbget('select * from stocks where puid=? and stock_name=?', (puid, stock_name))
    return rows[0] if rows else None

def create_holder_stock(puid, stock_name, count):
    dbinsert('insert into stocks(puid, stock_name, count) values (?,?,?)', (puid, stock_name, count,))

def update_holder_stock(puid, stock_name, count):
    dbupdate('update stocks set count=? where puid=? and stock_name=?', (count, puid, stock_name))

def get_stock_price(stock_name):
    rows = dbget('select count(*) n from weibos where date(timestamp) = ? and sender=?', (stock_newest_date(), stock_name,))
    if not rows:
        return 0
    return rows[0]['n']

def get_all_stocks():
    stock_names = get_all_senders()
    track_start_date = date_to_str(days_ago=10)
    return [(poster, get_weibos_with_poster_after_date(poster, track_start_date)) for poster in stock_names]

def stock_newest_date():
    return date_to_str(days_ago=1)