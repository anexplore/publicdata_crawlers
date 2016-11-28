# -*- coding: utf-8 -*-
"""
酷我排行榜歌曲下载
@author anexplore
"""
import json
import random
import sys
import time
import traceback
import urllib

import lxml.html
import tornado.httpclient as HttpClient


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5)' \
          ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
HEADERS = {}
HEADERS['User-Agent'] = USER_AGENT
HEADERS['Refer'] = 'http://www.kuwo.cn/'


def print_log(log_string):
    if not log_string:
        return
    sys.stdout.write('%s\n' % log_string)
    sys.stdout.flush()


class Song(object):
    """歌曲详细信息
    Attributes:
        name: 名称
        artist: 歌手
        album: 专辑
        pay: 收费
        song_id: 标识
        download_url: 下载地址
        play_url: 播放地址
        cover: 封面
    """

    def __init__(self):
        self.name = ''
        self.artist = ''
        self.album = ''
        self.pay = 0
        self.song_id = ''
        self.download_url = ''
        self.play_url = ''
        self.cover = ''

    def to_json_dict(self):
        return dict(
            name=self.name,
            artist=self.artist,
            album=self.album,
            pay=self.pay,
            song_id=self.song_id,
            download_url=self.download_url,
            play_url=self.play_url,
            covert=self.cover
        )

    def __str__(self):
        return json.dumps(self.to_json_dict(), ensure_ascii=False, encoding='UTF-8')


def crawl_download_url(song, http_client):
    """获取歌曲下载地址
    Args:
        song: 歌曲
    Returns:
        download url
    """
    if not song:
        return None
    params = dict(
        rid=song.song_id,
        type='convert_url',
        response='url',
        format='aac|mp3'
    )
    query = urllib.urlencode(params)
    request_url = 'http://antiserver.kuwo.cn/anti.s?%s' % query
    try:
        http_response = http_client.fetch(request_url, headers=HEADERS)
        return http_response.body
    except Exception as e:
        return None


def crawl_top_chart(chart_url, http_client):
    """抓取排行榜
    Args:
        chart_url: 排行榜地址
    Returns:
        yield Song
    """
    if not chart_url:
        return
    http_request = HttpClient.HTTPRequest(chart_url, request_timeout=30, headers=HEADERS)
    # 下载
    try:
        http_response = http_client.fetch(http_request)
    except Exception as e:
        print_log('download error' % str(e))
        return
    html_body = http_response.body
    root_node = lxml.html.document_fromstring(html_body.decode('utf-8'))
    song_nodes = root_node.xpath('//ul[@class="listMusic"]/li')
    for song_node in song_nodes:
        play_node = song_node.xpath('./div[@class="name"]/a/@href')
        play = '%s' % play_node[0]
        song_info_node = song_node.xpath('./div[@class="listRight"]/div[@class="tools"]/@data-music')
        song_info = '%s' % song_info_node[0]
        info_dict = json.loads(song_info)
        song = Song()
        song.play_url = play.decode('utf-8')
        song.album = info_dict.get('album', '')
        song.name = info_dict.get('name', '')
        song.song_id = info_dict.get('id', '')
        song.artist = info_dict.get('artist', '')
        song.pay = info_dict.get('pay', '0')
        yield song


http_client = HttpClient.HTTPClient()
urls = [
    'http://www.kuwo.cn/bang/content?name=%E9%85%B7%E6%88%91%E9%A3%99%E5%8D%87%E6%A6%9C',
    'http://www.kuwo.cn/bang/content?name=%E9%85%B7%E6%88%91%E6%96%B0%E6%AD%8C%E6%A6%9C',
    'http://www.kuwo.cn/bang/content?name=%E9%85%B7%E9%9F%B3%E4%B9%90%E6%B5%81%E8%A1%8C%E6%A6%9C',
]
dups = {}
try:
    for url in urls:
        print_log('process top chart:%s' % url)
        for song in crawl_top_chart(url, http_client):
            song.download_url = crawl_download_url(song, http_client)
            if not song.download_url:
                continue
            song_name = song.download_url[song.download_url.rfind('/') + 1:]
            if song_name in dups:
                continue
            try:
                http_request = http_client.fetch(song.download_url, request_timeout=180)
                f = open('songs/%s' % song_name, 'w')
                f.write(http_request.body)
                f.close()
                dups[song_name] = 0
                print_log('%d, write song %s:%s->%s' % (len(dups), song.name, song.song_id, song_name))
            except Exception as e:
                print traceback.format_exc()
            time.sleep(2 + random.randint(1, 3))
except HttpClient.HTTPError as e:
    print e
except Exception as e:
    print traceback.format_exc()
http_client.close()
