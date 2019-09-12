import os
import atexit
import shutil
import time
import requests
import re
from apscheduler.scheduler import Scheduler
from wxpy import Bot, ensure_one, embed

from weibo_api import get_timeline, process_status
from db import create_weibo_if_not_exists, get_weibo_with_wid, get_random_weibo

# Init wechat bot
bot = Bot(console_qr=True)
bot.messages.max_history = 1000

# Ensure wechat group exists in list (Can only get by name)
# required_group = 'testtest'
required_group = '姐(shǎ)夫(bī)观察小组'
while True:
    done = True
    if not bot.groups().search(required_group):
        done = False
    
    if not done:
        print("Not yet finished loading, try sending a message in the group.")
        time.sleep(5)
    else:
        print("Finished loading.")
        break


# Group
group = ensure_one(bot.groups().search(required_group))


# Crontab
sched = Scheduler()
print("Starting cron job...")
sched.start()


# Runs once per 5 minutes, get the statuses posted in past 5 minutes and send to grp
def job_function():
    statuses_to_send = get_timeline()
    if not statuses_to_send:
        return
    processed_statuses = [process_status(status) for status in statuses_to_send]
    for status in processed_statuses:
        exists, wid = create_weibo_if_not_exists(status) # Saves to db if not exist
        if not exists:
            send_weibo(status, wid)



sched.add_cron_job(job_function, minute='*/5')

# Sends a weibo to group
def send_weibo(status, wid=None):
    if not wid:
        wid = status.get('id', None)
    weibo_id_str = '' if not wid else ('\nWeibo ID: ' + str(wid))
    status_text = status['msg_body'] + weibo_id_str
    img_urls = status['img_urls']
    send_msg(status_text)

# Send message to grp
def send_msg(text):
    group.send(text)

# Send image to grp
# TODO: set a timeout
def send_img(url):
    img_path = "img_to_send.jpg"
    download_img(url, img_path)
    group.send_image(img_path)
    os.remove(img_path)

# Downloads an image from url and store at path
def download_img(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)




######################## Handle commands ########################
@bot.register(group, except_self=False)
def handle_msg(msg):
    msg_content = msg.text
    if not msg_content:
        return
    
    msg_content = msg_content.lower()

    searchweibo_pattern = re.compile("^ *search(?:weibo)? +(\\d+) *$")
    searchweibo_match = searchweibo_pattern.match(msg_content)
    if searchweibo_match:
        wid = int(searchweibo_match.groups()[0])
        weibo = get_weibo_with_wid(wid)
        if weibo:
            send_weibo(weibo)
        return

    randomweibo_pattern = re.compile("^ *random(?:weibo)? *$")
    randomweibo_match = randomweibo_pattern.match(msg_content)
    if randomweibo_match:
        weibo = get_random_weibo()
        if weibo:
            send_weibo(weibo)
        return
        
##################### End of handle commands ####################


# Shutdown crontab when web service stops
atexit.register(lambda: sched.shutdown(wait=False))

embed()
