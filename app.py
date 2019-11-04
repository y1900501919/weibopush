import os
import atexit
import shutil
import time
from datetime import datetime
import requests
import re
import random
from apscheduler.scheduler import Scheduler
from wxpy import Bot, ensure_one, embed

from weibo_api import get_timeline, process_status
from db import (
    create_weibo_if_not_exists, 
    get_random_weibo, 
    get_all_ratings,
    delete_weibo,
    recover_weibo
)
from command_utils import (
    rate,
    emo_rate,
    get_stats,
    attempt_create_alias,
    get_weibo_with_wid,
    search_weibos_with_kw,
    process_search_results,
    roll,
    roll_answer,
    replace_special,
    niwota,
    create_tss
)
from stocks import (
    get_user_info,
    get_stocks_info,
    buy_stocks,
    sell_stocks
)
from osu_utils import osurecent

TEST = False
REPEAT_RATE = 0.01

def set_repeat_rate(new_rate):
    global REPEAT_RATE
    REPEAT_RATE = min(max(0, new_rate), 0.45)

# Init wechat bot
bot = Bot(console_qr=True)
bot.messages.max_history = 1000

# Ensure wechat group exists in list (Can only get by name)
# required_group = 'testtest'
production_group_name = '姐(shǎ)夫(bī)观察小组'
my_test_group_name = 'bottest'
myself_name = 'Des'
required_chats = [production_group_name, my_test_group_name]

while True:
    done = True
    for required_chat in required_chats:
        if not bot.groups().search(required_chat):
            done = False
            print("Not yet finished loading {}, try sending a message in the {}.".format(required_chat, required_chat))
            break

    if not bot.friends().search(myself_name):
        done = False
        print("Not yet finished loading Des, try sending a message to Des.")
        
    if not done:
        time.sleep(5)
    else:
        print("Finished loading.")
        break


# Chats
production_group = ensure_one(bot.groups().search(production_group_name))
my_test_group = ensure_one(bot.groups().search(my_test_group_name))
myself = ensure_one(bot.friends().search(myself_name))


# Crontab
sched = Scheduler()
print("Starting cron job...")
sched.start()


# Run once per 5 minutes, get the statuses posted in past 5 minutes and send to grp
def get_new_status(send=True):
    statuses_to_send = get_timeline()
    if not statuses_to_send:
        return 0
    processed_statuses = [process_status(status) for status in statuses_to_send]
    new_list = []
    for status in processed_statuses:
        exists, wid = create_weibo_if_not_exists(status) # Saves to db if not exist
        if not exists:
            new_list.append((status, wid))

    if send:
        for (status, wid) in new_list[:3]:
            send_weibo(status, production_group, wid)

    return len(new_list)


sched.add_cron_job(get_new_status, minute='*/5')

# Sends a weibo to group
def send_weibo(status, chat=None, wid=None):
    if not wid:
        wid = status.get('id', None)
    weibo_id_str = '' if not wid else ('\nWeibo ID: ' + str(wid))

    feedback_str = ''
    if wid:
        feedbacks = get_all_ratings(wid)
        if feedbacks:
            feedback_str = ''
            ratings = [x['rating'] for x in feedbacks if x['rating'] >= 0]
            if ratings:
                feedback_str += '\nRating: {}'.format(sum(ratings) * 1.0 / len(ratings))
            emos = [x['emo'] for x in feedbacks if x['emo']]
            if emos:
                feedback_str += '\n' + ''.join(emos)
        else:
            feedback_str = '\n这条微博还没有评分，快来"rate {} [0-5]"或者"emo {} [emoji]"成为第一个评分的人吧¿'.format(wid, wid)
    
    status_text = datetime.strptime(status['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%Y/%m/%d, %a, %H:%M:%S') + '\n' + status['sender'] + '\n' + status['msg_body'] + '\n' + status['link'] + '\n' + weibo_id_str + feedback_str
    send_msg(status_text, chat)

# Send message to grp
def send_msg(text, chat=None):
    if not chat:
        my_test_group.send(text)
    else:
        chat.send(text)

# Send image to grp
# TODO: set a timeout
def send_img(url):
    img_path = "img_to_send.jpg"
    download_img(url, img_path)
    production_group.send_image(img_path)
    os.remove(img_path)

def send_local_img(path, chat):
    chat.send_image(path)

# Downloads an image from url and store at path
def download_img(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)


######################## Handle commands ########################
@bot.register([production_group, my_test_group], except_self=False)
def handle_msg(msg):
    chat = msg.chat
    msg_content = msg.text
    sender = msg.sender
    sender_name = sender.nick_name
    if not msg_content:
        return

    if TEST:
        if chat != my_test_group:
            send_msg("Testing testing", chat)
            return

    searchweibo_pattern = re.compile("^ *search(?:weibo)? +(\\d+) *$", re.IGNORECASE)
    searchweibo_match = searchweibo_pattern.match(msg_content)
    if searchweibo_match:
        wid = int(searchweibo_match.groups()[0])
        weibo = get_weibo_with_wid(wid)
        if weibo:
            send_weibo(weibo, chat)
        else:
            send_msg("Dun have weibo ID: {}".format(wid), chat)
        return

    searchweibo_kw_pattern = re.compile("^ *search(?:weibo)?((?: +(?:\\w|[\U00010000-\U0010ffff])+)+) *$", re.IGNORECASE)
    searchweibo_kw_match = searchweibo_kw_pattern.match(msg_content)
    if searchweibo_kw_match:
        keywords = searchweibo_kw_match.groups()[0].strip().split(' ')
        weibo_lst = search_weibos_with_kw(keywords)
        if weibo_lst:
            if len(weibo_lst) == 1:
                send_weibo(weibo_lst[0], chat)
            else:
                search_results = process_search_results(weibo_lst, keywords)
                send_msg(search_results, chat)
        else:
            send_msg("Dun have weibos with these keywords", chat)
        return

    randomweibo_pattern = re.compile("^ *random(?:weibo)? *$", re.IGNORECASE)
    randomweibo_match = randomweibo_pattern.match(msg_content)
    if randomweibo_match:
        weibo = get_random_weibo()
        if weibo:
            send_weibo(weibo, chat)
        return

    roll_pattern = re.compile("^ *roll(?: +(\d+))?(?: +(\d+))?(?: +(\d+))? *$", re.IGNORECASE)
    roll_match = roll_pattern.match(msg_content)
    if roll_match:
        grps = roll_match.groups()
        reply = None
        if grps[2]:
            reply = roll(int(grps[0]), int(grps[1]), n=int(grps[2]))
        elif grps[1]:
            reply = roll(int(grps[0]), int(grps[1]))
        elif grps[0]:
            reply = roll(0, int(grps[0]))
        else:
            reply = roll(0, 100)
        
        if reply:
            send_msg(reply, chat)
        
        return

    roll_answer_pattern = re.compile("^ *roll(?: +(?:[\w？\\?]+))((?: +(?:\w+))+) *$", re.IGNORECASE|re.MULTILINE|re.UNICODE)
    roll_answer_match = roll_answer_pattern.match(msg_content)
    if roll_answer_match:
        answers = roll_answer_match.groups()[0].strip().split(' ')
        send_msg(roll_answer(answers), chat)
        return

    
    rate_score_pattern = re.compile("^ *rate +(\d+) +([0-5]) *$", re.IGNORECASE)
    rate_score_match = rate_score_pattern.match(msg_content)
    if rate_score_match:
        wid = int(rate_score_match.groups()[0])
        rating = int(rate_score_match.groups()[1])
        reply = rate(wid, rating, sender_name)
        send_msg(reply, chat)
        return
    
    
    emo_pattern = re.compile("^ *emo +(\d+) +([\U00010000-\U0010ffff]+) *$", re.IGNORECASE|re.UNICODE)
    emo_match = emo_pattern.match(msg_content)
    if emo_match:
        wid = int(emo_match.groups()[0])
        emo = emo_match.groups()[1]
        reply = emo_rate(wid, emo, sender_name)
        send_msg(reply, chat)
        return 

    
    delete_pattern = re.compile("^ *delete +(\d+) *$", re.IGNORECASE)
    delete_match = delete_pattern.match(msg_content)
    if delete_match:
        wid = int(delete_match.groups()[0])
        delete_weibo(wid)
        send_msg("Deleted weibo {}".format(wid), chat)
        return

    recover_pattern = re.compile("^ *recover +(\d+) *$", re.IGNORECASE)
    recover_match = recover_pattern.match(msg_content)
    if recover_match:
        wid = int(recover_match.groups()[0])
        recover_weibo(wid)
        send_msg("Recoverd weibo {}".format(wid), chat)
        return

    pulle_pattern = re.compile("^ *pulle *$", re.IGNORECASE)
    pulle_match = pulle_pattern.match(msg_content)
    if pulle_match:
        count = get_new_status(send=False)
        if not count:
            send_msg("No new weibo.", chat)
        else:
            send_msg("Pulled {} weibos.".format(count), chat)
        return

    stats_pattern = re.compile("^ *stats +(\\w+)(?: +(\\d+))? *$", re.IGNORECASE)
    stats_match = stats_pattern.match(msg_content)
    if stats_match:
        poster_name = stats_match.groups()[0]
        days_back = stats_match.groups()[1]
        stats_img_path = get_stats(poster_name, days_back)
        if stats_img_path:
            send_local_img(stats_img_path, chat)
        else:
            send_msg("No data.", chat)
        return


    alias_pattern = re.compile("^ *alias +(\\w+) *= *(\\w+) *$", re.IGNORECASE)
    alias_match = alias_pattern.match(msg_content)
    if alias_match:
        alias = alias_match.groups()[0]
        name = alias_match.groups()[1]
        save_result = attempt_create_alias(alias, name)
        send_msg(save_result, chat)
        return

    me_pattern = re.compile("^ *me *$", re.IGNORECASE)
    me_match = me_pattern.match(msg_content)
    if me_match:
        me_info = get_user_info(sender_name)
        send_msg(me_info, chat)
        return

    stocks_pattern = re.compile("^ *stocks *$", re.IGNORECASE)
    stocks_match = stocks_pattern.match(msg_content)
    if stocks_match:
        stocks_img_path = get_stocks_info()
        if stocks_img_path:
            send_local_img(stocks_img_path, chat)
        else:
            send_msg('No data.', chat)
        return

    stocks_buy_pattern = re.compile("^ *stocks +buy +(\\w+) +(\\d+) *$", re.IGNORECASE)
    stocks_buy_match = stocks_buy_pattern.match(msg_content)
    if stocks_buy_match:
        stock_name = stocks_buy_match.groups()[0]
        count = int(stocks_buy_match.groups()[1])
        buy_result_message = buy_stocks(sender_name, stock_name, count)
        send_msg(buy_result_message, chat)
        return

    stocks_sell_pattern = re.compile("^ *stocks +sell +(\\w+) +(\\d+) *$", re.IGNORECASE)
    stocks_sell_match = stocks_sell_pattern.match(msg_content)
    if stocks_sell_match:
        stock_name = stocks_sell_match.groups()[0]
        count = int(stocks_sell_match.groups()[1])
        sell_result_message = sell_stocks(sender_name, stock_name, count)
        send_msg(sell_result_message, chat)
        return

    ping_pattern = re.compile("^ *ping *$", re.IGNORECASE)
    ping_match = ping_pattern.match(msg_content)
    if ping_match:
        send_msg("pong", chat)
        return

    osurecent_pattern = re.compile("^ *osurecent(?: +(\w+))? *$", re.IGNORECASE)
    osurecent_match = osurecent_pattern.match(msg_content)
    if osurecent_match:
        osu_username = osurecent_match.groups()[0]
        send_msg(osurecent(osu_username), chat)
        return

    tss_pattern = re.compile("^ *tss +(.+) *$", re.IGNORECASE)
    tss_match = tss_pattern.match(msg_content)
    if tss_match:
        tss = tss_match.groups()[0]
        create_tss(tss.strip())
        production_group.send_image("ts.png")
        return

    ###########################  Sudo ###########################
    sudo_pattern = re.compile(" *sudo (.+) *$", re.IGNORECASE)
    sudo_match = sudo_pattern.match(msg_content)
    sudo_msg = ''
    if sudo_match:
        if sender != myself:
            send_msg('请发送‘好爸爸’来获取sudo权限。', chat)
            return
        sudo_msg = sudo_match.groups()[0]
        

    set_repeat_rate_pattern = re.compile("^ *set repeat rate (0(?:\\.\d+)?) *$", re.IGNORECASE)
    set_repeat_rate_match = set_repeat_rate_pattern.match(sudo_msg)
    if set_repeat_rate_match:
        set_repeat_rate(float(set_repeat_rate_match.groups()[0]))
        send_msg('复读概率已设置为{}'.format(REPEAT_RATE), chat)
        return

    ######################## End of Sudo ########################


    # 你我他复读机，放最后

    special_repeat_prob, msg_content = replace_special(msg_content)
    repeat_prob = REPEAT_RATE
    if '你' in msg_content or '我' in msg_content:
        repeat_prob *= 3
        repeat_prob = min(repeat_prob, 0.8)
    if random.random() <= repeat_prob:
        niwotarepeat = niwota(msg_content)
        if niwotarepeat:
            send_msg(niwotarepeat, chat)
            return

    if random.random() < special_repeat_prob:
        send_msg(msg_content, chat)
        return
        
##################### End of handle commands ####################


# Shutdown crontab when web service stops
atexit.register(lambda: sched.shutdown(wait=False))

embed()
