# -*- coding: utf-8 -*-
# @Time    : 2022/6/4 10:33
# @Author  : hertx
# @Software: PyCharm
# @File    : http.py
import sys
import time
import json
from functools import wraps
from typing import Union, List
from requests import Session, Response, exceptions
from requests.cookies import cookiejar_from_dict
from requests.structures import CaseInsensitiveDict
from requests.packages import urllib3
from lxml import etree, html

# 关闭错误提示
urllib3.disable_warnings()

__all__ = [
    "http",
    "Http",
    "random_chrome_version",
    "func_run_times",
]
if sys.version_info >= (3,):
    from urllib.parse import urlencode
    from urllib import parse
else:
    from urllib import urlencode, parse


def random_chrome_version():
    import random
    version_list = ['85.0.4183.83', '85.0.4183.87', '86.0.4240.22', '87.0.4280.20', '87.0.4280.88',
                    '88.0.4324.96', '89.0.4389.23', '90.0.4430.24', '91.0.4472.19', '90.0.4430.212']
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{} ' \
                 'Safari/537.36 '
    return user_agent.format(random.choice(version_list))


def func_run_times(lenth: int = 3):
    """
    函数运行耗时装饰器
    :param lenth:默认3位小数
    :return:
    """
    """
    # @functools.wraps(func),这是python提供的装饰器。
    # 它能把原函数的元信息拷贝到装饰器里面的 func 函数中。函数的元信息包括docstring,name,参数列表等等
    # 可以尝试去除@functools.wraps(func),你会发现"func".__name__的输出变成了inter
    # 经过装饰后实质上是得到的函数体是wrapper
    @func_run_times()
    def a():
        ...
    print(a.__name__)
    """

    def wrapper(fn):
        # from functools import wraps

        def print_red(string):
            print(f"\033[36m{string}\033[0m")

        # @wraps(fn)
        def inter(*args, **kwargs):
            start = time.time()
            res = fn(*args, **kwargs)
            print_red("run time of the func is '%s' %.*f Ms" % (fn.__name__, lenth, (time.time() - start) * 1000))
            return res

        return inter

    return wrapper


def requests_catch_exception(func):
    """
    requests异常捕获装饰器
    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Union[HTTPResponse, HTTPError]:
        try:
            return func(*args, **kwargs)
        except exceptions.HTTPError:
            return HTTPError(1000, 'HTTP错误!')
        except exceptions.SSLError:
            return HTTPError(1001, 'SSL错误!')
        except exceptions.ProxyError:
            return HTTPError(1002, '代理错误!')
        except exceptions.ConnectTimeout:
            return HTTPError(1003, '请求响应超时!')
        except exceptions.ConnectionError:
            return HTTPError(1004, '网络连接错误!')
        except exceptions.ChunkedEncodingError:
            return HTTPError(1005, 'chunked编码错误!')
        except exceptions.ContentDecodingError:
            return HTTPError(1006, '内部解码错误!')
        except Exception as e:
            return HTTPError(1007, e)

    return wrapper


class HTTPResponse(object):

    def __init__(self, response: Response):
        """
        :param response:http响应请求体
        """
        self.ok = True
        self.__html = None
        self.__response = response
        self.code = response.status_code
        if response.encoding and response.encoding.lower() in ['iso-8859-1', 'gb2312']:
            """
            部分页面没有编码"说明"，无法检测到编码类型,如果默认编码在常用编码类型之外将强制转化为最常见的gbk编码
            也可手动更改或使用apparent_encoding做自适应
            虽然默认编码是GB2312,但是实际上使用的是GBK编码 且 GB2312 是 GBK子集
            """
            self.encoding = 'GBK'

    def apparent_encoding(self):
        """
        应用自适应检测网页编码,会大幅度降低速度且不能做到完全匹配
        """
        self.encoding = self.__response.apparent_encoding
        if self.encoding.lower() == 'gb2312':
            self.encoding = 'GBK'
        return self.encoding

    @property
    def encoding(self):
        return self.__response.encoding

    @encoding.setter
    def encoding(self, encode):
        self.__response.encoding = encode

    @property
    def json(self) -> dict:
        if (3,) <= sys.version_info < (3, 6):
            return json.loads(self.res.content.decode(self.encoding), encoding=self.encoding)
        return self.__response.json()

    @property
    def lxml(self):
        from bs4 import BeautifulSoup
        return BeautifulSoup(self.__response.text, "lxml")

    def xpath(self, *args) -> List[html.HtmlElement]:
        self.__html = self.__html if self.__html is not None else etree.HTML(self.text)
        return self.__html.xpath(*args)

    @property
    def text(self):
        return self.__response.text

    @property
    def content(self):
        return self.__response.content

    @property
    def res(self):
        return self.__response

    def xml2dict(self, xml_data=None) -> dict:
        import xmltodict
        dict_xml = xmltodict.parse(xml_data) if xml_data else xmltodict.parse(self.text.encode("utf-8"))
        return json.loads(json.dumps(dict_xml))

    def dict2xml(self, json_str: Union[dict, str] = None):
        json_str = json_str if json_str else self.json
        if isinstance(json_str, str):
            json_str = json.loads(json_str)
        if len(json_str.keys()) > 1:
            json_str = {'root': json_str}
        import xmltodict
        return xmltodict.unparse(json_str, pretty=1)

    def __str__(self):
        return "{}:{}".format(self.__response, self.encoding)


class HTTPError(object):
    """请求错误"""

    def __init__(self, code, reason=None):
        """
        :param code: http状态码
        :param reason: http状态原因
        """
        super().__init__()
        self.ok = False
        self.code = code
        self.reason = reason

    def __str__(self):
        return "HTTP {}: {}".format(self.code, self.reason)


class Http(object):
    """基于requests 方便日常使用的简单二次封装"""

    def __init__(self, ignore_status=True):
        """
        :param ignore_status: 是否忽略错误状态码
        """
        self.__http = Session()
        self.ignore_status = ignore_status
        self.__http.headers.update({"User-Agent": random_chrome_version()})

    def get(self, url, params=None, timeout=None, proxies=None, **kwargs):
        """
        GET请求
        """
        kwargs.setdefault('allow_redirects', True)
        return self.request('GET', url, params=params, timeout=timeout, proxies=proxies, **kwargs)

    def post(self, url, data=None, timeout=None, proxies=None, **kwargs):
        """
        POST请求
        """
        return self.request('POST', url, data=data, timeout=timeout, proxies=proxies, **kwargs)

    @requests_catch_exception
    def request(self, method, url, **kwargs):
        """
        :param method: 大小不敏感，在Session内部upper统一转化为大写
        :param url: 地址
        :param kwargs:
        :return:
        """
        with self.__http.request(method, url, **kwargs) as r:
            results = HTTPResponse(r)
        if not self.ignore_status and results.code != 200:
            return HTTPError(results.code, '请求状态错异常!')
        return results

    @property
    def cookies(self) -> dict:
        """
        读取cookies
        """
        _cookies = {}
        [_cookies.update({k: v}) for k, v in self.__http.cookies.items()]
        return _cookies

    @cookies.setter
    def cookies(self, cookie: dict):
        """
        设置cookies
        """
        self.__http.cookies = cookiejar_from_dict(cookie)

    @property
    def headers(self) -> CaseInsensitiveDict:
        self.__http.headers.items()
        return self.__http.headers

    @headers.setter
    def headers(self, header: dict or str):
        self.__http.headers.clear()
        self.add_headers(header)

    def add_headers(self, header: dict or str) -> CaseInsensitiveDict:
        if isinstance(header, str):
            header = self._raw_headers_to_dict(header)
        if isinstance(header, dict):
            return [self.__http.headers.update({k: v}) for k, v in header.items()].clear() or self.__http.headers

    @staticmethod
    def _raw_headers_to_dict(this_headers_str: str) -> dict:
        """
        抓包raw字符串解析为headers
        :param this_headers_str:
        :return:
        """
        """
        results = {}
        for item in this_headers_str.strip().split('\n'):
            if not item.strip():
                continue
            items = item.strip().split(':')
            results[items[0]] = ':'.join(items[1:]).strip()
        return results
        """
        # lambda
        return (lambda x: [[(lambda xx: (
            lambda items: [xx.update({items[0].strip(): ':'.join(items[1:]).strip()}), xx][1]))(x)(
            item.strip().split(':')) for item in this_headers_str.strip().split('\n') if item.strip()], x])(dict())[1]

    @staticmethod
    def dict2url(dict_params) -> str:
        """
        字典转url
        :param dict_params:
        :return:
        """
        return urlencode(dict_params)

    @staticmethod
    def quote(content, encoding='utf-8', **kwargs):
        """
        url编码
        """
        return parse.quote(content, encoding=encoding, **kwargs)

    @staticmethod
    def unquote(content, encoding='utf-8', **kwargs):
        """
        url解码
        """
        return parse.unquote(content, encoding=encoding, **kwargs)


http = Http()
