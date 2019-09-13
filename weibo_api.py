import json
import time
import requests
from pytz import timezone
from datetime import datetime


# Weibo API
APP_KEY = "2815647836"
APP_SECRET = "52fcbb03a2ec45d54fd5c4b40a9582ba"
ACCESS_TOKENS = ["2.00UICb9GmcKYED184c921789UvEILB", "2.00UICb9GjN2laD17d8d8ed46m3MqiC", "2.00UICb9GJq9MNEcfa105c155Ym6k5C", "2.00UICb9GxtYSiBb7f3f1cfff8pOxYB", "2.00UICb9G0KIRMv93790c41bd0IBVtN", "2.00UICb9GIK3NhB50cb97aab8gTTwQD"]
WEIBO_API_TIME_FORMAT = "%a %b %d %H:%M:%S %z %Y"
REQUEST_URL = "https://api.weibo.com/2/statuses/home_timeline.json"
WEIBOLINK = "https://m.weibo.cn/status/"




# Get statuses in past 5 minutes
def get_timeline():
    url = REQUEST_URL
    response_text = None
    for i, access_token in enumerate(ACCESS_TOKENS):
        get_params = {"access_token": access_token, "count": 100}
        response = requests.get(url, params=get_params)
        if (response.status_code == 200):
            print("Using token {}: {} to query".format(i, access_token))
            response_text = response.text
            break

    if not response_text:
        print("All tokens are limited.")
        return

    response_json = json.loads(response_text)
    statuses = response_json['statuses']

    statuses_new = []
    for status in statuses:
        timestr = status['created_at']
        created_timestamp = datetime.strptime(timestr, WEIBO_API_TIME_FORMAT).replace(tzinfo=timezone('Asia/Singapore'))
        created_secs = time.mktime(created_timestamp.timetuple())
        statuses_new.append(status)
    
    return statuses_new

# Process a status json obj to formatted text and image urls
def process_status(status):
    content = status['text']
    timestr = status['created_at']
    post_uid = status['user']['id']
    weibo_id = status['id']
    user_link = WEIBOLINK + str(weibo_id)
    poster_username = status['user']['name']
    created_timestamp = datetime.strptime(timestr, WEIBO_API_TIME_FORMAT)
    formatted_timestr = datetime.strftime(created_timestamp, '%Y/%m/%d, %a, %H:%M:%S')

    msg_body = formatted_timestr + '\n' + poster_username + '\n' + content + '\n' + user_link
    img_urls = [x['thumbnail_pic'].replace('thumbnail', 'large') for x in status['pic_urls']]

    result = dict()
    result['msg_body'] = msg_body
    result['post_uid'] = post_uid
    result['weibo_id'] = weibo_id
    result['img_urls'] = img_urls
    return result