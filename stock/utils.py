#coding=utf-8
"""
Tools
@author caoliuyi
"""

import urllib2

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X10_11_0)'
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36')


def http_fetch(url, data=None, headers=None):
    """
    Args:
        url: url address
        data: post data
        headers: headers
    Return:
        code, body, headers_dict
    """
    if not url:
        return -1, None, None
    try:
        if headers is None:
            headers = {}
        if 'User-Agent' not in headers:
            headers['User-Agent'] = USER_AGENT
        request = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(request)
        return response.getcode(), response.read(), response.info()
    except Exception as e:
        print "http_fetch error:%s" % str(e)
    finally:
        if response is not None:
            response.close()
    return -1, None, None
