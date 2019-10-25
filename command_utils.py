import random
from datetime import datetime, timedelta

from plot import plot_status_history
from db import (
    search_weibo,
    get_weibo_with_wid, 
    get_weibo_feedback, 
    update_weibo_feedback_rating, 
    save_weibo_feedback_rating, 
    update_weibo_feedback_emo,
    save_weibo_feedback_emo,
    get_weibos_with_poster_after_date,
    check_symbol_is_poster,
    check_alias_exists,
    save_alias,
    unalias,
    get_name_from_alias
)

def attempt_create_alias(alias, name):
    if check_symbol_is_poster(alias):
        return "Alias {} is a weibo poster.".format(alias)
    if check_alias_exists(alias):
        return "Alias {} already exists.".format(alias)
    if not check_symbol_is_poster(name):
        return "Name {} is not a weibo poster.".format(name)
    save_alias(alias, name)
    return "Successfuly set {}'s alias to \"{}\"".format(name, alias)


def get_stats(poster_name, days_back=None):
    poster_name = unalias(poster_name)
    if not days_back:
        days_back = 10
    else:
        days_back = int(days_back)
    days_back = min(max(days_back, 1), 30)
    date_N_days_ago = (datetime.now() - timedelta(days=days_back)).date().strftime('%Y-%m-%d %H:%M:%S')
    stats = get_weibos_with_poster_after_date(poster_name, date_N_days_ago)
    if not stats:
        return None
    dates = [datetime.strptime(x['day'], '%Y-%m-%d').strftime('%m/%d') for x in stats]
    values = [x['n'] for x in stats]
    plot_status_history(dates, values, 'STATS OF {}'.format(poster_name), 'stats.png')
    return 'stats.png'

def search_weibos_with_kw(keywords):
    keywords = [x.strip() for x in keywords]
    return search_weibo(keywords)

def process_search_results(weibo_lst, keywords):
    result = '{} Results.'.format(len(weibo_lst))
    for weibo in weibo_lst:
        wid = weibo['id']
        content = weibo['msg_body']
        ctx_length = 4;
        for keyword in keywords:
            if keyword not in content: continue
            idx = content.index(keyword)
            idx_start = max(idx-ctx_length, 0)
            idx_end = min(idx+ctx_length+len(keyword), len(content)-1)
            context = [x.strip() for x in content[idx_start:idx_end].split('\n') if keyword in x][0]
            result += '\n{}: ...'.format(wid) + context + '...'
    return result


def roll(a, b, n=1):
    if a > b:
        a, b = b, a

    if n > 20:
        return "Maximum roll count is 20, your input is {}".format(n)

    return ', '.join([str(random.randint(a, b)) for _ in range(n)])

def roll_answer(answers):
    return random.choice(answers).strip()

def niwota(msg):
    msg = msg.replace('你', '他')
    msg = msg.replace('我', '你')
    return msg

def rate(wid, rating, sender_puid):
    weibo = get_weibo_with_wid(wid)
    if not weibo:
        return "weibo ID: {} dun have".format(wid)
    
    existing_feedback = get_weibo_feedback(wid, sender_puid)
    if (existing_feedback):
        existing_rating = existing_feedback['rating']
        update_weibo_feedback_rating(wid, rating, sender_puid)
        if existing_rating >= 0:
            return "Your rating for weibo ID: {} has been changed: {} => {}".format(wid, existing_rating, rating)
        else:
            return "Your rating for weibo ID: {} is: {}".format(wid, rating)
    else:
        save_weibo_feedback_rating(wid, rating, sender_puid)
        return "Your rating for weibo ID: {} is: {}".format(wid, rating)


def emo_rate(wid, emo, sender_puid):
    weibo = get_weibo_with_wid(wid)
    if not weibo:
        return "weibo ID: {} dun have, hwat r u doing ah".format(wid)

    existing_feedback = get_weibo_feedback(wid, sender_puid)
    if existing_feedback:
        existing_emo = existing_feedback['emo']
        update_weibo_feedback_emo(wid, emo, sender_puid)
        if existing_emo:
            return "Your emo for weibo ID: {} has been changed: {} => {}".format(wid, existing_emo, emo)
        else:
            return "Your emo for weibo ID: {} is: {}".format(wid, emo)
    else:
        save_weibo_feedback_emo(wid, emo, sender_puid)
        return "Your emo for weibo ID: {} is: {}".format(wid, emo)


def replace_special(msg_content):
    # Fixed
    if msg_content == '好爸爸':
        return 1, '好儿子'

    # Replace
    prob = 0
    if msg_content[0] in ['他', '她']:
        prob = 0.03
        msg_content = random.choice(['对，', '对啊，', '对哦，']) + msg_content
    if '老白' in msg_content:
        prob = 1
        msg_content = msg_content.replace('老白', random.choice(['PekTohNee', 'Pek Pek', 'Pekky', 'Pekiro']))
    if '白' in msg_content:
        prob = 1
        msg_content = msg_content.replace('白', 'pek')
    if '头神' in msg_content:
        prob = 1
        msg_content = msg_content.replace('头神', random.choice(['我们的主', '我们的上帝', 'God', '頭神様', '我们的圣上', '我们的王', '我们的红太阳', '绝对强者', '天之骄子・木易']))
    return prob, msg_content
