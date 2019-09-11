import json
import time
import requests
from pytz import timezone
from datetime import datetime


# Weibo API
APP_KEY = "2815647836"
APP_SECRET = "52fcbb03a2ec45d54fd5c4b40a9582ba"
ACCESS_TOKEN = "2.00UICb9GmcKYED184c921789UvEILB"
WEIBO_API_TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"
REQUEST_URL = "https://api.weibo.com/2/statuses/home_timeline.json"
WEIBOLINK = "weibo.com/u/"


# Get statuses in past 10 minutes
def get_timeline():
    url = REQUEST_URL
    get_params = {"access_token": ACCESS_TOKEN, "count": 100}
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
        
        statuses_new.append(status)
        # if (time_diff <= 600):
        #     statuses_new.append(status)
        # else:
        #     break
    
    return statuses_new

# Process a status json obj to formatted text and image urls
def process_status(status):
    content = status['text']
    timestr = status['created_at']
    post_uid = status['user']['id']
    user_link = WEIBOLINK + str(post_uid)
    poster_username = status['user']['name']
    created_timestamp = datetime.strptime(timestr, WEIBO_API_TIME_FORMAT)
    formatted_timestr = datetime.strftime(created_timestamp, '%Y/%m/%d, %a, %H:%M:%S')

    msg_body = formatted_timestr + '\n' + poster_username + '\n' + content + '\n' + user_link
    weibo_id = status['id']
    img_urls = [x['thumbnail_pic'].replace('thumbnail', 'middle') for x in status['pic_urls']]

    result = dict()
    result['msg_body'] = msg_body
    result['post_uid'] = post_uid
    result['weibo_id'] = weibo_id
    result['img_urls'] = img_urls
    return result