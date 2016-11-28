#coding=utf-8
"""
Sina Stock Channel's API
@author caoliuyi
"""

from __future__ import absolute_import

import json

import stock.utils as utils

def astock_list(page_index=1, count=40):
    """
    所有A股股票
    Args:
        page_index: 索引
        count: 每页数量
    Returns:
        股票列表: 股票总数,本次返回数,[(股票标示, 股票代码, 股票名称)]
    """
    if page_index < 0:
        page_index = 1
    if count < 0:
        count = 1
    url = 'http://money.finance.sina.com.cn/d/api/openapi_proxy.php/?' \
          '__s=[[%22hq%22,%22hs_a%22,%22%22,0,{0},{1}]]&callback='.format(str(page_index), str(count))
    code, body, headers = utils.http_fetch(url)
    if code < 200:
        return []
    body = body.decode('utf-8')
    response_list = json.loads(body)
    if len(response_list) == 0:
        return []
    response = response_list[0]
    if response['code'] != 0:
        return []
    items = response['items']
    count = len(items)
    total_count = response['count']
    stock_list = []
    for stock in items:
        stock_list.append((stock[0], stock[1],stock[2]))
    return total_count, count, stock_list


def stock_hq(symbol):
    """
    股票行情
    Args:
        symbol: 股票标示
    Returns:
        股票行情: [名称, 开盘价, 收盘价, 当前价, 最高价, 最低价, 买一价, 卖一价,
                  成交量, 成交额, 买一数, 买一价, 买二数, 买二价, 买三数,
                  买三价, 买四数, 买四价, 买五数, 买五价, 卖一量, 卖一价,
                  卖二量, 卖二价, 卖三量, 卖三价, 卖四量, 卖四价, 卖五价,
                  卖五量, 日期, 时间, 00]
    """
    if not symbol:
        return []
    url = 'http://hq.sinajs.cn/list=%s' % symbol
    code, body, headers = utils.http_fetch(url)
    body = body.decode('GBK')
    start_pos = body.find('"')
    end_pos = body.rfind('"')
    data_string = body[start_pos + 1 : end_pos]
    return data_string.split(',')


def stocks_hq(symbol_list_string):
    """
    Args:
        symbol_list: sh600059,sh600059
    Returns:
         股票行情列表: [[x,x,x....], [x,x,x,....]]
    """
    result = []
    if not symbol_list_string:
        return result
    url = 'http://hq.sinajs.cn/list=%s' % symbol_list_string
    code, body, headers = utils.http_fetch(url)
    body = body.decode('GBK')
    body_field = body.split(';')
    for field in body_field:
        field = field.strip()
        if not field:
            continue
        start_pos = field.find('"')
        end_pos = field.rfind('"')
        data_string = field[start_pos + 1 : end_pos]
        result.append(data_string.split(','))
    return result
