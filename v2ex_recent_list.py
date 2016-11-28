#coding=utf-8
"""
采集v2ex recent主贴地址
@author caoliuyi
@date
"""

import json
import random
import shelve
import sys
import time
import urllib2

import lxml
import lxml.html


def log(string):
    if not string:
        return
    sys.stdout.write('%s %s\n' % (time.strftime('%Y-%m-%d %H:%M:%S',
                                  time.localtime()), string))
    sys.stdout.flush()


def parse(decoded_html_body):
    doc = lxml.html.document_fromstring(decoded_html_body)
    for item in doc.xpath('//div[@class="cell item"]'):
        try:
            user_url = item.xpath('.//td[1]/a/@href')[0]
            user_img = item.xpath('.//td[1]/a/img/@src')[0]
            title = item.xpath('.//td[3]/span/a/text()')[0]
            title_url = item.xpath('.//td[3]/span/a/@href')[0]
            if title_url and title_url.find('#') > 0:
                title_url = title_url[:title_url.find('#')].strip()
            status_id = title_url[title_url.rfind('/') + 1:]
            node_name = item.xpath('.//td[3]/span[2]/a[1]/text()')[0]
            node_url = item.xpath('.//td[3]/span[2]/a[1]/@href')[0]
            user_name = item.xpath('.//td[3]/span[2]/strong/a/text()')[0]
            result = {}
            user = {}
            user['name'] = user_name
            user['image'] = 'https:%s' % user_img
            user['home'] = 'https://www.v2ex.com%s' % user_url
            result['user'] = user
            status = {}
            status['id'] = status_id
            status['title'] = title
            status['url'] = 'https://www.v2ex.com%s' % title_url
            result['status'] = status
            node = {}
            node['url'] = 'https://www.v2ex.com%s' % node_url
            node['name'] = node_name
            result['node'] = node
            yield result
        except Exception as e:
            pass


def download(url):
    for i in range(3):
        try:
            headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) '\
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            req = urllib2.Request(url, headers=headers)
            response = urllib2.urlopen(req, timeout=30)
            content = response.read()
            content = content.decode('utf-8')
            return content
        except:
            time.sleep(3)
    return None


def main(out_path, dup_path):
    url = 'https://www.v2ex.com/recent?p={page}'
    page = 1
    fail_count = 0
    f = open(out_path, 'a')
    dup = shelve.open(dup_path)
    while True:
        cur_url = url.replace('{page}', '%d' % page)
        log('start to process:%s' % cur_url)
        body = download(cur_url)
        if body:
            count = 0
            if fail_count > 0:
                fail_count -= 1
            else:
                fail_count = 0
            for result in parse(body):
                if result['status']['id'] in dup:
                    continue
                dup[result['status']['id']] = 1
                dup.sync()
                count += 1
                try:
                    f.write('%s\n' % json.dumps(result, ensure_ascii=False).encode('utf-8'))
                    f.flush()
                except Exception as e:
                    log(str(e))
                    pass
            if count == 0:
                log('all done, jump to first page')
                page = 0
        else:
            fail_count += 1
            if fail_count > 10:
                log('too many failed, break')
                break
        time.sleep(3 + random.randint(1, 10))
        page += 1
    log('Page:%d' % page)
    f.close()
    dup.close()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Error params'
        sys.exit(-1)
    out_path = sys.argv[1]
    dup_path = sys.argv[2]
    main(out_path, dup_path)

