# -*- coding: utf-8 -*-
import random
import re
import sys
import time
import urllib2

import lxml
import lxml.html as Parser

ershoufang_url_pattern = 'http://bj.lianjia.com/ershoufang/hu1pg{number}y2/'
ershoufang_new_online_pattern = 'http://bj.lianjia.com/ershoufang/hu1pg{number}tt2y2/'
headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36' \
                        ' (KHTML, like Gecko) Chrome/53.0.2785.89 Safari/537.36'
HID_PATTERN = re.compile(r'(\d+).html')
AREA_PATTERN = re.compile(r'([\d.]+)平米'.decode('utf-8'))


class House(object):

    def __init__(self):
        #编码
        self.house_code = ''
        #标题
        self.title = ''
        #首页
        self.house_home_page = ''
        #图片
        self.cover_pic = ''
        #社区名称
        self.community_name = ''
        #地区
        self.district = ''
        #厅数
        self.blueprint_hall_num = 0
        #卧室数
        self.blueprint_bedroom_num = 0
        #面积
        self.area = 0.0
        #总价
        self.price = 0
        #单价
        self.unit_price = 0
        #朝向
        self.orientation = ''
        #百度地图
        self.baidu_la = 0.0
        self.baidu_lo = 0.0
        #标签
        self.tags = []
        #标签
        self.color_tags = []
        #挂牌时间
        self.se_ctime = 0


def download(url, headers):
    try:
        request = urllib2.Request(url, headers=headers)
        response = urllib2.urlopen(request, timeout=30)
        if response.code != 200:
            return None
        return response.read().decode('utf-8')
    except Exception as e:
        sys.stderr.write(str(e) + '\n')
    finally:
        if response:
            response.close()
    return None


def extract_list(url, html):
    """
    抽取二手房列表页
    """
    list_xpath = '//ul[@class="sellListContent"]/li'
    document = Parser.document_fromstring(html)
    house_list = document.xpath(list_xpath)
    for house_node in house_list:
        title = '%s' % house_node.xpath('.//div[@class="title"]/a/text()')[0]
        house_link = '%s' % house_node.xpath('.//div[@class="title"]/a/@href')[0]
        house_id = HID_PATTERN.search(house_link).group(1)
        community = '%s' % house_node.xpath('.//div[@class="houseInfo"]/a/text()')[0]
        house_info = '%s' % house_node.xpath('.//div[@class="houseInfo"]/text()')[0]
        area = AREA_PATTERN.search(house_info).group(1)
        district = '%s' % house_node.xpath('.//div[@class="positionInfo"]/a/text()')[0]
        price = '%s' % house_node.xpath('.//div[@class="totalPrice"]/span/text()')[0]
        unit_price = '%s' % house_node.xpath('.//div[@class="unitPrice"]/@data-price')[0] 
        sys.stdout.write(('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (title, house_id, area, price, unit_price,
                         house_link, community, district)).encode('utf-8'))
        sys.stdout.flush()


def all_list_page(url_pattern):
    page = 1
    while page <= 100:
        sys.stderr.write('page:%d\n' % page)
        page_url = url_pattern.replace('{number}', str(page))
        for x in range(10):
            html_content = download(page_url, headers)
            if not html_content:
                time.sleep(2)
                continue
            break    
        extract_list(page_url, html_content)
        page += 1
        time.sleep(random.random())


def all_house():        
    all_list_page(ershoufang_url_pattern)


def all_new_online_house():
    all_list_page(ershoufang_new_online_pattern)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        all_house()
        sys.exit()
    if sys.argv[1] == 'all':
        all_house()
        sys.exit()
    elif sys.argv[1] == 'new':
        all_new_online_house()
    else:
        all_house() 
