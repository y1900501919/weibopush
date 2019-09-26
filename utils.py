from datetime import datetime, timedelta

def date_to_str(date_format='%Y-%m-%d', days_ago=None):
    result_datetime = datetime.now()
    if days_ago:
        result_datetime -= timedelta(days=days_ago)
    return result_datetime.date().strftime(date_format)