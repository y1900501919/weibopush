from weibo_api import get_timeline
from db import create_weibo_if_not_exists

def get_statuses(page):
    statuses = get_timeline(page=page)
    return statuses