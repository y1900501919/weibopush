import requests

APP_KEY = ["2815647836", "3291629583", "3859594497", "1570715685", "845176942", "1554698740"]
APP_SECRET = ["52fcbb03a2ec45d54fd5c4b40a9582ba", "b23db2906e93082f54b85a439fa0ddda", "aefb24e6ee4ac8b5034ddd9f7d51a640", "6b00b75c912af063f8ccb27e0305f097", "2dc89c9f76ac8e2befc73a2fd83e67b9", "6899a278d277f5dd000a5d810c0b854c"]
REDIRECT_URI = "https://api.weibo.com/oauth2/default.html"

def get_code(i):
    url = "https://api.weibo.com/oauth2/authorize?client_id={}&redirect_uri={}&response_type=code".format(APP_KEY[i], REDIRECT_URI)
    print(url)

def get_token(i, code):
    url = "https://api.weibo.com/oauth2/access_token"
    post_data = {'client_id': APP_KEY[i], 'client_secret': APP_SECRET[i],
                 'code': code, 'redirect_uri': REDIRECT_URI}
    response = requests.post(url, data=post_data)
    print(response.text)

