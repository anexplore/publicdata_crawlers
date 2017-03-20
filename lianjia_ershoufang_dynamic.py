# -*- coding: utf-8 -*-
"""
爬取链家二手房简要信息
@author caoliuyi
"""
import json
import re
import time

import lxml
import lxml.html
import requests
import requests.exceptions

MOBILE_USER_AGENT = ['User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '\
                                   'Chrome/56.0.2924.87 Safari/537.36']
X_REQUEST_WITH = ['X-Requested-With', 'XMLHttpRequest']

PRICE_UNIT_PTN = re.compile(r'(\d+)元/平'.decode('UTF-8'))

ID_PTN = re.compile(r'(\d+)\.html'.decode('UTF-8'))


class House(object):
    """房子信息
    Attributes:
        self.xx
    """

    def __init__(self):
        # 编码
        self.house_code = ''
        # 标题
        self.title = ''
        # 首页
        self.house_home_page = ''
        # 图片
        self.cover_pic = ''
        # 社区名称
        self.community_name = ''
        # 地区
        self.district = ''
        # 厅数
        self.blueprint_hall_num = 0
        # 卧室数
        self.blueprint_bedroom_num = 0
        # 面积
        self.area = 0.0
        # 总价
        self.price = 0
        # 单价
        self.unit_price = 0
        # 朝向
        self.orientation = ''
        # 百度地图
        self.baidu_la = 0.0
        self.baidu_lo = 0.0
        # 标签
        self.tags = []
        # 标签
        self.color_tags = []
        # 挂牌时间
        self.se_ctime = 0
        # 描述
        self.description = ''


def download(url, headers=None, encoding='UTF-8', timeout=20, retry_count=3):
    """下载
    :param url: 请求地址
    :param headers: http头
    :param encoding: 网页编码
    :param timeout: 超时时间
    :param retry_count: 重试次数
    :return: 下载后的网页正文 下载失败返回None
    """
    response = None
    for retry in xrange(retry_count):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            if response.status_code == 200:
                response.encoding = encoding
                return response.text
        except requests.exceptions.Timeout as timeout:
            continue
        except requests.exceptions.RequestException as requestException:
            return None
        finally:
            if response:
                response.close()


def next_page_builder(max_page=100):
    """生成下一个网页地址
    :return: 下一页地址
    """
    for i in xrange(1, max_page + 1):
        yield 'https://m.lianjia.com/bj/ershoufang/pg%d/?_t=1' % i


def request(url):
    """请求网页内容
    :param url: 链家网页地址
    :return: 网页内容
    """
    headers = {}
    headers[MOBILE_USER_AGENT[0]] = MOBILE_USER_AGENT[1]
    headers[X_REQUEST_WITH[0]] = X_REQUEST_WITH[1]
    headers['Referer'] = url
    response = download(url, headers=headers, timeout=30, retry_count=5)
    if not response:
        return None
    try:
        json_obj = json.loads(response, encoding='UTF-8')
        return json_obj.get('body', None)
    except Exception as e:
        return None


def get_node_text(node):
    """获取Node节点的文本
    :param node:
    :return: 文本
    """
    if node is None:
        return ''
    texts = []
    for text in node.itertext():
        texts.append('%s' % text)
    return ''.join(texts)


def extract_price_unit(text):
    """抽取单价
    :param text: 单价文本
    :return: 单价
    """
    match = PRICE_UNIT_PTN.match(text)
    if match > 0:
        return match.group(1)


def extract_house_code(text):
    """抽取房屋编码
    :param text: 房屋编码
    :return: 编码
    """
    match = ID_PTN.search(text)
    if match > 0:
        return match.group(1)


def parse(html_content):
    """解析网页内容抽取House
    :param html_content: 网页内容
    :return: House
    """
    if not html_content:
        yield None
    doc = lxml.html.document_fromstring(html_content)
    house_li_nodes = doc.xpath('/html/body/li')
    for house_node in house_li_nodes:
        url_nodes = house_node.xpath('.//a/@href')
        url = '' if not url_nodes else '%s' % url_nodes[0]
        if url:
            house_code = extract_house_code(url)
            url = 'http://bj.lianjia.com/ershoufang/%s.html' % house_code
        else:
            continue
        cover_nodes = house_node.xpath('.//div[@class="media_main"]/img/@src')
        cover = '' if not cover_nodes else ('%s' % cover_nodes[0])
        title_nodes = house_node.xpath('.//div[@class="item_list"]/div[@class="item_main"]')
        title = '' if not title_nodes else get_node_text(title_nodes[0])
        desc_nodes = house_node.xpath('.//div[@class="item_list"]/div[@class="item_other text_cut"]')
        desc = '' if not desc_nodes else get_node_text(desc_nodes[0])
        price_nodes = house_node.xpath('.//div[@class="item_list"]/div[@class="item_minor"]'
                                       '/span[@class="price_total"]/em')
        price = 0 if not price_nodes else int(get_node_text(price_nodes[0]))
        price_unit_nodes = house_node.xpath('.//div[@class="item_list"]/div[@class="item_minor"]'
                                            '/span[@class="unit_price"]')
        price_unit = 0 if not price_unit_nodes else int(extract_price_unit(get_node_text(price_unit_nodes[0])))
        tag_nodes = house_node.xpath('.//div[@class="item_list"]/div[@class="tag_box"]/span')
        tags = []
        for tag_node in tag_nodes:
            tags.append(get_node_text(tag_node))
        house = House()
        house.house_code = house_code
        house.house_home_page = url
        house.title = title
        house.cover_pic = cover
        house.price = price
        house.unit_price = price_unit
        house.color_tags = tags
        house.description = desc
        yield house

for url in next_page_builder(20):
    for house in parse(request(url)):
        if not house:
            break
        print '%s\t%s\t%d\t%s' % (house.house_code, house.title, house.price, house.house_home_page)

