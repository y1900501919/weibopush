import requests
import json
from datetime import datetime
from dateutil import tz

def get_recent(username):
    url = "https://osu.ppy.sh/api/get_user_recent?k=6475b4d38db5cc1beee024f272d40ef371c9856d&u={}&limit=1".format(username)
    t = json.loads(requests.get(url).text)[0]['date']
    fmt = '%Y-%m-%d %H:%M:%S'
    dt = datetime.strptime(t, fmt)
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    dt=dt.replace(tzinfo=from_zone)
    dt=dt.astimezone(to_zone)
    return "{}: {}".format(username, dt.strftime(fmt))

def get_all_recents():
    userlist = ["fuko2", "LeafBell"]
    return '\n'.join([get_recent(x) for x in userlist])

def osurecent(username=None):
    if not username:
        return get_all_recents()
    return get_recent(username)