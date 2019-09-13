import os
import atexit
import shutil
import time
import requests
import re
import random
from apscheduler.scheduler import Scheduler
from wxpy import Bot, ensure_one, embed

from weibo_api import get_timeline, process_status
from db import create_weibo_if_not_exists, get_weibo_with_wid, get_random_weibo, get_weibo_feedback, update_weibo_feedback, save_weibo_feedback

TEST = True

# Init wechat bot
bot = Bot(console_qr=True)
bot.enable_puid()
bot.messages.max_history = 1000

# Ensure wechat group exists in list (Can only get by name)
# required_group = 'testtest'
production_group_name = '姐(shǎ)夫(bī)观察小组'
test_group_name = 'testtest'
myself_name = 'bottest'
required_chats = [production_group_name, test_group_name, myself_name]

while True:
    done = True
    for required_chat in required_chats:
        if not bot.groups().search(required_chat):
            done = False
            print("Not yet finished loading {}, try sending a message in the {}.".format(required_chat, required_chat))
            break
    
    if not done:
        time.sleep(5)
    else:
        print("Finished loading.")
        break


# Chats
production_group = ensure_one(bot.groups().search(production_group_name))
test_group = ensure_one(bot.groups().search(test_group_name))
myself = ensure_one(bot.groups().search(myself_name))


# Crontab
sched = Scheduler()
print("Starting cron job...")
sched.start()


# Runs once per 5 minutes, get the statuses posted in past 5 minutes and send to grp
def get_new_status():
    statuses_to_send = get_timeline()
    if not statuses_to_send:
        return
    processed_statuses = [process_status(status) for status in statuses_to_send]
    for status in processed_statuses:
        exists, wid = create_weibo_if_not_exists(status) # Saves to db if not exist
        if not exists:
            send_weibo(status, wid)



sched.add_cron_job(get_new_status, minute='*/5')

# Sends a weibo to group
def send_weibo(status, chat=None, wid=None):
    if not wid:
        wid = status.get('id', None)
    weibo_id_str = '' if not wid else ('\nWeibo ID: ' + str(wid))
    status_text = status['msg_body'] + weibo_id_str
    img_urls = status['img_urls']
    send_msg(status_text, chat)

# Send message to grp
def send_msg(text, chat=None):
    if not chat:
        myself.send(text)
    else:
        chat.send(text)

# Send image to grp
# TODO: set a timeout
# def send_img(url):
#     img_path = "img_to_send.jpg"
#     download_img(url, img_path)
#     production_group.send_image(img_path)
#     os.remove(img_path)

# Downloads an image from url and store at path
def download_img(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)




######################## Handle commands ########################
@bot.register([production_group, test_group, myself], except_self=False)
def handle_msg(msg):
    chat = msg.chat
    msg_content = msg.text
    sender_puid = msg.sender.puid
    if not msg_content:
        return

    if TEST:
        if chat != myself:
            send_msg("Testing testing", chat)
            return

    searchweibo_pattern = re.compile("^ *search(?:weibo)? +(\\d+) *$", re.IGNORECASE)
    searchweibo_match = searchweibo_pattern.match(msg_content)
    if searchweibo_match:
        wid = int(searchweibo_match.groups()[0])
        weibo = get_weibo_with_wid(wid)
        if weibo:
            send_weibo(weibo, chat)
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
        reply = rate(wid, rating, sender_puid)
        send_msg(reply, chat)
        return


    # 你我他复读机，放最后
    if random.random() >= 0.9:
        niwotarepeat = niwota(msg_content)
        if niwotarepeat:
            send_msg(niwotarepeat, chat)
        
        return



def roll(a, b, n=1):
    if a > b:
        a, b = b, a

    if n > 20:
        return "Maximum roll count is 20, your input is {}".format(n)

    return ', '.join([str(random.randint(a, b)) for _ in range(n)])

def roll_answer(answers):
    return random.choice(answers).strip()

def niwota(msg):
    msg = msg.replace('他', '<#T##>')
    msg = msg.replace('你', '他')
    msg = msg.replace('我', '你')
    msg = msg.replace('<#T##>', '我')
    return msg

def rate(wid, rating, sender_puid):
    weibo = get_weibo_with_wid(wid)
    if not weibo:
        return "weibo ID: {} dun have".format(wid)
    
    existing_feedback = get_weibo_feedback(wid, sender_puid)
    if (existing_feedback):
        existing_rating = existing_feedback['rating']
        update_weibo_feedback(wid, rating, sender_puid)
        return "Your rating for weibo ID: {} has been changed: {} => {}".format(wid, existing_rating, rating)
    else:
        save_weibo_feedback(wid, rating, sender_puid)
        return "Your rating for weibo ID: {} is: {}".format(wid, rating)

        
##################### End of handle commands ####################


# Shutdown crontab when web service stops
atexit.register(lambda: sched.shutdown(wait=False))

embed()
