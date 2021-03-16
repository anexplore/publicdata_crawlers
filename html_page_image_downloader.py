# -*- coding: utf-8 -*-
"""
下载某个网页中的所有图片
"""
import imghdr
import os.path
import traceback
import sys
import urllib.parse

import lxml.html
import requests

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip'
}

# {'http': '', 'https': ''}
PROXIES = None
ENCODING = 'utf8'

page_url = sys.argv[1]
img_dir = sys.argv[2]

if not os.path.exists(img_dir):
    os.makedirs(img_dir)

print('will download image from %s to %s' % (page_url, img_dir))


def find_next_file_index(filenames):
    max_index = 0
    if not filenames:
        return max_index
    for filename in filenames:
        prefix, _ = filename.split('.')
        try:
            prefix = int(prefix)
            if prefix > max_index:
                max_index = prefix
        except:
            pass
    return max_index + 1


def resolve_absolute_url(base_url, relative_url):
    try:
        return urllib.parse.urljoin(base_url, relative_url)
    except:
        return relative_url


def download(url, headers=None, timeout=20, proxies=None, stream=False, retries=3, encoding='utf8'):
    if headers is None:
        headers = DEFAULT_HEADERS
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, proxies=proxies, timeout=timeout, stream=stream)
            if not response.ok:
                return None
            if not stream:
                response.encoding = encoding
                return response.text
            else:
                return [thunk for thunk in response.iter_content(chunk_size=None)]
        except requests.exceptions.RequestException:
            print('requests occurs error %s' % traceback.format_exc())
    return None


def html_page_extractor(html_content, base_url):
    document = lxml.html.document_fromstring(html_content)
    urls = []
    for image_src in document.xpath('//img[@src]/@src'):
        urls.append(resolve_absolute_url(base_url, image_src))
    return urls


page_content = download(page_url, proxies=PROXIES, encoding=ENCODING)
if page_content is None:
    print('download failed')
    sys.exit(0)
image_srcs = html_page_extractor(page_content, page_url)
print('may be have %s images' % len(image_srcs))
file_index = find_next_file_index(os.listdir(img_dir))
crawled = set()
for url in image_srcs:
    if not url:
        continue
    if url in crawled:
        continue
    file_index += 1
    crawled.add(url)
    print('try to download image %s' % url)
    contents = download(url, proxies=PROXIES, stream=True)
    if not contents:
        print('download failed for %s' % url)
        continue
    file_type = imghdr.what(None, contents[0])
    if file_type is None:
        file_type = 'jpg'
    file_index_string = ('%s' % file_index).zfill(5)
    save_path = os.path.join(img_dir, '%s.%s' % (file_index_string, file_type))
    with open(save_path, 'wb') as image_file:
        for content in contents:
            image_file.write(content)
    print('save to %s' % save_path)
print('all done')