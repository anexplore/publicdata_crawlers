# -*- coding: utf-8 -*-
"""
知乎用户遍历
"""
import json
import shelve
import sys
import random
import time
import traceback
import Queue
import urllib

import lxml.html
import tornado.httpclient as httpclient


headers = {}
headers['Cookie'] = 'Your Cookie'
headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)' \
                        ' Chrome/51.0.2704.103 Safari/537.36'
headers['X-Xsrftoken'] = 'Your Token'
headers['Origin'] = 'https://www.zhihu.com'
post_dict = {}
post_dict['method'] = 'next'
params = dict(
    offset=0,
    order_by='created',
    hash_id='user hash id'
)
start_url = 'https://www.zhihu.com/people/liu-peng-cheng-sai-l/followees'


def print_log(string):
    sys.stdout.write('%s\n' % string)
    sys.stdout.flush()


class ZhiHuUser(object):

    def __init__(self):
        self.name = ''
        self.description = ''
        self.url = ''
        self.hash_id = ''
        self.followee_num = 0
        self.follower_num = 0
        self.like_num = 0
        self.question_num = 0
        self.answer_num = 0

    def to_json_dict(self):
        return dict(
            name=self.name,
            description=self.description,
            url=self.url,
            hash_id=self.hash_id,
            followee_num=self.followee_num,
            follower_num=self.follower_num,
            like_num=self.like_num,
            question_num=self.question_num,
            answer_num=self.answer_num
        )


def get_hashid(url, http_client):
    """抓取HashId
    :param url: 用户首页地址
    :return: hash_id
    """
    headers['Referer'] = url
    request = httpclient.HTTPRequest(url, headers=headers, request_timeout=60)
    response = None
    for i in range(3):
        try:
            response = http_client.fetch(request)
            break
        except:
            time.sleep(3)
    if response is None:
        return None
    doc = lxml.html.document_fromstring(response.body)
    data_node = doc.xpath('//script[@data-name="current_people"]/text()')
    if not data_node:
        return None
    data = '%s' % data_node[0]
    data_list = json.loads(data)
    return data_list[3] if len(data_list) == 4 else None


def fetch_followees(user):
    """抓取关注者
    :param: user
    :return: yield user
    """
    offset = 0

    params['hash_id'] = user.hash_id
    headers['Referer'] = user.url
    url = 'https://www.zhihu.com/node/ProfileFolloweesListV2'
    while True:
        print_log('fetch offset:%d' % offset)
        params['offset'] = offset
        post_dict['params'] = json.dumps(params)
        body = urllib.urlencode(post_dict)
        headers['Content-Length'] = len(body)
        request = httpclient.HTTPRequest(url, method='POST', headers=headers, body=body,
                                         request_timeout=60, validate_cert=False)
        response = None
        for i in range(3):
            try:
                response = http_client.fetch(request)
                break
            except:
                print_log(traceback.format_exc())
                time.sleep(random.randint(1, 3))
        if response is None:
            return
        try:
            response_dict = json.loads(response.body)
            user_list = response_dict.get('msg')
            if len(user_list) == 0:
                return
            offset += len(user_list)
            for user_html in user_list:
                doc = lxml.html.document_fromstring(user_html)
                user = ZhiHuUser()
                user.hash_id = doc.xpath('//div/div[@class="zg-right"]/button/@data-id')[0]
                user.name = doc.xpath('//div[@class="zm-list-content-medium"]/h2/a/@title')[0]
                user.url = doc.xpath('//div[@class="zm-list-content-medium"]/h2/a/@href')[0]
                user.description = doc.xpath('//div[@class="zm-list-content-medium"]/div[@class="zg-big-gray"]/text()')
                user.description = '' if len(user.description) == 0 else user.description[0]
                followers_text = doc.xpath('//div[@class="zm-list-content-medium"]/div[@class="details zg-gray"]/a[1]/text()')[0]
                user.follower_num = int(followers_text.split()[0])
                question_text = doc.xpath('//div[@class="zm-list-content-medium"]/div[@class="details zg-gray"]/a[2]/text()')[0]
                answer_text = doc.xpath('//div[@class="zm-list-content-medium"]/div[@class="details zg-gray"]/a[3]/text()')[0]
                like_text = doc.xpath('//div[@class="zm-list-content-medium"]/div[@class="details zg-gray"]/a[4]/text()')[0]
                user.question_num = int(question_text.split()[0])
                user.answer_num = int(answer_text.split()[0])
                user.like_num = int(like_text.split()[0])
                yield user
            time.sleep(random.randint(1, 6))
        except:
            print_log(traceback.format_exc())
            return

http_client = httpclient.HTTPClient()
start_user = ZhiHuUser()
start_user.hash_id = 'start user hash id'
start_user.url = 'start user home page url'
f = open('user.txt', 'a')
dup = shelve.open('dup.dat')
queue = Queue.Queue()
queue.put(start_user)
while not queue.empty():
    u = queue.get()
    print_log('start to process:%s' % u.url)
    for user in fetch_followees(u):
        if user.hash_id in dup:
            continue
        dup[user.hash_id] = 0
        queue.put(user)
        f.write('%s\n' % json.dumps(user.to_json_dict(), ensure_ascii=False).encode('utf-8'))
        f.flush()

f.close()
dup.close()
http_client.close()
