# -*- coding: utf-8 -*-
"""
采集鬼吹灯小说
"""
import random
import sys
import time

import tornado.httpclient
import lxml.html

home_page = 'http://www.luoxia.com/guichui/'
#修改此处 选择 第几部
book_name_xpath = '//*[@id="gcd-8"]/a/text()'
#修改此处 选择 章节列表
book_chapter_list = '//*[@id="content-list"]/div[18]/ul/li/a/@href'

######一下无需修改######
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36' \
     ' (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
client = tornado.httpclient.HTTPClient()
home_page_content = client.fetch(home_page, user_agent=user_agent).body
document = lxml.html.document_fromstring(home_page_content)
book_title = document.xpath(book_name_xpath)
if not book_title:
    print 'No Book Title'
    sys.exit(1)

book_title = '%s' % book_title[0]
out = open('%s.txt' % book_title, 'w')


def merge_text(node_list):
    return ''.join(node_list)


book_chapter_list = document.xpath(book_chapter_list)
for url in book_chapter_list:
    for x in range(4):
        try:
            html = client.fetch(url, user_agent=user_agent, request_timeout=60)
            break
        except:
            time.sleep(5)
    if html is None:
        print 'Error'
        break
    chapter_doc = lxml.html.document_fromstring(html.body)
    chapter_title = '%s' % chapter_doc.xpath('//*[@id="pagewrap"]/article/header/h1/text()')[0]
    chapter_content_list = chapter_doc.xpath('//*[@id="pagewrap"]/article/p')
    chapter_content_list = [merge_text(x.xpath('.//text()')) for x in chapter_content_list]
    chapter_content = '\r\n    '.join(chapter_content_list)
    print chapter_content.encode('utf-8')
    out.write('\r\n%s\r\n    %s' % (chapter_title.encode('utf-8'), chapter_content.encode('utf-8')))
    out.flush()
    time.sleep(2 + random.random())


print 'Finish'
out.close()
client.close()