from flask import Flask
from flask_restful import Resource, Api

import os
import requests
import atexit
import json
import time
import shutil
from datetime import datetime
from apscheduler.scheduler import Scheduler
from pytz import timezone

from wxpy import Bot, ensure_one, embed

app = Flask(__name__)

# Weibo API
APP_KEY = "2815647836"
APP_SECRET = "52fcbb03a2ec45d54fd5c4b40a9582ba"
ACCESS_TOKEN = "2.00UICb9GmcKYED184c921789UvEILB"
WEIBO_API_TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"
REQUEST_URL = "https://api.weibo.com/2/statuses/home_timeline.json"
WEIBOLINK = "weibo.com/u/"

# Init wechat bot
bot = Bot(console_qr=True)
bot.messages.max_history = 1000

# Ensure wechat group exists in list (Can only get by name)
# required_groups = ['testtest']
required_groups = ['姐(shǎ)夫(bī)观察小组']
while True:
    done = True
    for grp in required_groups:
        if not bot.groups().search(grp):
            done = False
    
    if not done:
        print("Not yet finished loading, try sending a message in the group.")
        time.sleep(5)
    else:
        print("Finished loading.")
        break


# Group
group = ensure_one(bot.groups().search(required_groups[0]))


# Crontab
sched = Scheduler()
print("Starting cron job...")
sched.start()


# Runs once per 10 minutes, get the statuses posted in past 10 minutes and send to grp
def job_function():
    statuses_to_send = get_timeline()
    if not statuses_to_send:
        return
    processed_statuses = [process_status(status) for status in statuses_to_send]
    for status_text, img_urls in processed_statuses:
        send_msg(status_text)
        _ = [send_img(x) for x in img_urls]


sched.add_cron_job(job_function, minute='*/10')


# Send message to grp
def send_msg(text):
    group.send(text)

# Send image to grp
def send_img(url):
    img_path = "img_to_send.jpg"
    download_img(url, img_path)
    group.send_image(img_path)
    os.remove(img_path)

def download_img(url, path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(path, 'wb') as f:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, f)


# Process a status json obj to formatted text and image urls
def process_status(status):
    content = status['text']
    timestr = status['created_at']
    user_link = WEIBOLINK + str(status['id'])
    created_timestamp = datetime.strptime(timestr, WEIBO_API_TIME_FORMAT)
    formatted_timestr = datetime.strftime(created_timestamp, '%Y/%m/%d, %A, %H:%M:%S')
    img_urls = [x['thumbnail_pic'].replace('thumbnail', 'middle') for x in status['pic_urls']]
    return formatted_timestr + ':\n' + content + '\n' + user_link, img_urls


# Get statuses in past 10 minutes
def get_timeline():
    url = REQUEST_URL
    get_params = {"access_token": ACCESS_TOKEN}
    response = requests.get(url, params=get_params)
    if (response.status_code != 200):
        # TODO: handle
        return

    response_json = json.loads(response.text)
    statuses = response_json['statuses']

    statuses_new = []
    for status in statuses:
        timestr = status['created_at']
        created_timestamp = datetime.strptime(timestr, WEIBO_API_TIME_FORMAT).replace(tzinfo=timezone('Asia/Singapore'))
        created_secs = time.mktime(created_timestamp.timetuple())
        time_diff = time.time() - created_secs
        if (time_diff <= 600):
            statuses_new.append(status)
        else:
            break
    
    return statuses_new
        


# Shutdown crontab when web service stops
atexit.register(lambda: sched.shutdown(wait=False))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port="9000", use_reloader=False)
    embed()
