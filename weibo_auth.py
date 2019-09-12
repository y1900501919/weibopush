import requests

APP_KEY = "2815647836"
APP_SECRET = "52fcbb03a2ec45d54fd5c4b40a9582ba"
REDIRECT_URI = "https://api.weibo.com/oauth2/default.html"
# GET CODE:
# https://api.weibo.com/oauth2/authorize?client_id=2815647836&redirect_uri=https://api.weibo.com/oauth2/default.html&response_type=code
CODE = "0b83b6de40795b56320c2460c2565bc5"


def get_token():
    url = "https://api.weibo.com/oauth2/access_token"
    post_data = {'client_id': APP_KEY, 'client_secret': APP_SECRET,
                 'code': CODE, 'redirect_uri': REDIRECT_URI}
    response = requests.post(url, data=post_data)
    return response

