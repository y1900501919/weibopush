from db import (
    unalias,
    create_stockholder,
    get_stockholder,
    update_stockholder,
    get_holder_stocks,
    get_holder_stock,
    create_holder_stock,
    update_holder_stock,
    get_all_stocks,
    get_stock_price,
)

def get_user_info(puid):
    info = "My puid: {}".format(puid)
    if not get_stockholder(puid):
        create_stockholder(puid)
    
    stockholder = get_stockholder(puid)
    info += '\nMoney: ${}'.format(stockholder['money'])

    stocks = get_holder_stocks(puid)
    if stocks:
        for stock in stocks:
            info += '\n{}: {} stocks'.format(stock['stock_name'], stock['count'])
    else:
        info += '\nNo stocks'
    return info


def get_stocks_info():
    stocks_info = get_all_stocks()
    info = '- TODAY\'S STOCKS -'
    for (k, v) in stocks_info.items():
        money = '-' if v <= 0 else '${}'.format(v)
        info += '\n{}: {}'.format(k, money)
    
    return info

def buy_stocks(puid, stock_alias, count):
    stock_name = unalias(stock_alias)
    price = get_stock_price(stock_name)
    if price <= 0:
        return 'Cannot buy this stock.'

    if not get_stockholder(puid):
        create_stockholder(puid)

    stockholder = get_stockholder(puid)
    price_sum = price * count
    money = stockholder['money']
    if money < price_sum:
        return 'You have ${}, cannot afford {} stocks of {}.'.format(money, count, stock_alias)

    money -= price_sum
    update_stockholder(puid, money)
    stocks = get_holder_stock(puid, stock_name)
    if not stocks:
        create_holder_stock(puid, stock_name, count)
    else:
        stock_count = stocks['count'] + count
        update_holder_stock(puid, stock_name, stock_count)
    
    return "Successfully bought {} stocks of {}.".format(count, stock_alias)

def sell_stocks(puid, stock_alias, count):
    stock_name = unalias(stock_alias)
    price = get_stock_price(stock_name)
    if price <= 0:
        return 'Cannot sell this stock.'

    if count <= 0:
        return 'Cannot sell {} stocks.'.format(count)

    if not get_stockholder(puid):
        create_stockholder(puid)

    stockholder = get_stockholder(puid)
    stocks = get_holder_stock(puid, stock_name)
    if not stocks:
        return 'You never bought {} before.'.format(stock_alias)

    stock_count = stocks['count']
    if stock_count < count:
        return 'You only have {} stocks of {}.'.format(stock_count, stock_alias)

    update_holder_stock(puid, stock_name, stock_count - count)
    price_sum = price * count
    money = stockholder['money']
    money += price_sum
    update_stockholder(puid, money)
    
    return "Successfully sold {} stocks of {}.".format(count, stock_alias)