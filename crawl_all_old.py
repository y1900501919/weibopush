from datetime import datetime
from weibo_api import get_timeline, process_status
from db import create_weibo_if_not_exists

def get_statuses(page):
    statuses = get_timeline(page=page)
    return statuses

def run():
    n = 1;
    while True:
        count = 0
        statuses = get_statuses(n)
        if not statuses: return
        processed_statuses = [process_status(status) for status in statuses]
        for status in processed_statuses:
            exists, wid = create_weibo_if_not_exists(status)
            if exists:
                count += 1;
        
        print("Saved {} new entries".format(count))
        
