# -*- coding: utf-8 -*-
"""
从 http://music.163.com/#/discover/playlist 拉取所有歌单
@author caoliuyi
"""
import sys
import time
import traceback
import urllib2

import lxml.html

DEFAULT_HEADERS = {}
DEFAULT_HEADERS['Referer'] = 'http://music.163.com/'
DEFAULT_HEADERS['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2)' \
                                ' AppleWebKit/537.36 (KHTML, like Gecko)' \
                                ' Chrome/55.0.2883.95 Safari/537.36'
DEFAULT_HEADERS['Connection'] = 'close'
# 全部
url_prefix = 'http://music.163.com/discover/playlist/?order=hot&cat=%E5%85%A8%E9%83%A8&' \
             'limit=35&offset={offset}'


def parse(body):
    doc = lxml.html.document_fromstring(body)
    nodes = doc.xpath('//ul[@class="m-cvrlst f-cb"]/li')
    for node in nodes:
        href = '%s' % node.xpath('.//a[@class="msk"]/@href')[0]
        title = '%s' % node.xpath('.//a[@class="msk"]/@title')[0]
        play_count = '%s' % node.xpath('.//span[@class="nb"]/text()')[0]
        pos = play_count.find('万'.decode('utf-8'))
        if pos > 0:
            play_count = int(play_count[0:pos]) * 10000
        else:
            play_count = int(play_count)
        yield (title, play_count, 'http://music.163.com/#%s' % href)


offset = 0
while 1:
    url = url_prefix.replace("{offset}", "%d" % offset)
    try:
        request = urllib2.Request(url, headers=DEFAULT_HEADERS)
        response = urllib2.urlopen(request, timeout=30)
        response_body = response.read()
        response.close()
        #parse
        count = 0
        for title, play_count, href in parse(response_body):
            count += 1
            sys.stdout.write('%s\t%d\t%s\n' % (title, play_count, href))
            sys.stdout.flush()
        offset += 35
        time.sleep(1)
        if count < 35:
            break
    except Exception as e:
        print traceback.format_exc()