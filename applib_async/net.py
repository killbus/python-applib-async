"""..."""
from dataclasses import dataclass
from typing import Generic, List, Union
import json
#-#from datetime import datetime
#-#from datetime import timedelta
#-#import time
import os
#-#import redis
#-#import random
#-#from getpass import getuser
#-#from urllib.parse import urlparse
#-#from urllib.parse import urljoin
#-#from urllib.parse import parse_qs
#-#from lxml import etree
import asyncio
from asyncio import BaseEventLoop
import aiohttp
import aiodns
#-#import configparser
#-#import codecs
#-#from difflib import SequenceMatcher
#-#from aiohttp.errors import ClientTimeoutError
#-#from aiohttp.errors import ClientConnectionError
#-#from aiohttp.errors import ClientDisconnectedError
#-#from aiohttp.errors import ContentEncodingError
from aiohttp import ClientError
#-#from aiohttp.errors import HttpBadRequest
#-#from aiohttp.errors import ClientHttpProcessingError
from aiohttp.resolver import AsyncResolver
from aiohttp.client_reqrep import RequestInfo
#-#from setproctitle import setproctitle
#-#import subprocess
#-#import concurrent
#-#import signal
#-#import re
#-#import multiprocessing
#-#import execjs
#-#import webbrowser
#-#from .audio_lib import PlaySound
#-#from .qrcode_lib import QrCode
#-#from .watch_lib import startWatchConf, stopWatchConf
#-#from .filter_lib import FilterTitle
#-#from .coupon_lib import CouponManager
#-#from .db_lib import HistoryDB
#-#from .db_lib import Item
#-#from .orm_lib import HistoryDB
#-#from .tools_lib import htmlentitydecode
import traceback
from .types.DataClass import DataClass, DataType
from .types.Null import Null
from .tools import pcformat

from .logu import logger
info, debug, warn, error = logger.info, logger.debug, logger.warning, logger.error


class NetManager(object):
    """网络请求功能简单封装
    """

    def __init__(self, loop: BaseEventLoop=None):
        self.loop = loop
        self.sess = None

    async def _get_session(self, *args, **kwargs):
        """..."""
#-#        resolver = AsyncResolver(nameservers=['8.8.8.8', '8.8.4.4', '1.1.1.1'])
#-#        conn = aiohttp.TCPConnector(resolver=resolver, limit=10, ttl_dns_cache=300)
        conn = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300)
        headers = kwargs.pop('headers', {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36'})
        if self.loop:
            self.sess = aiohttp.ClientSession(*args, connector=conn, headers=headers, loop=self.loop, **kwargs)
        else:
            self.sess = aiohttp.ClientSession(*args, connector=conn, headers=headers, **kwargs)

        info('sess inited.')

    async def __call__(self, *args, **kwargs):
        """..."""
        await self._get_session(*args, **kwargs)

    async def debug_log(self, response: aiohttp.ClientResponse):
        """打印错误日志, 便于分析调试"""
        r: RequestInfo = response.request_info()
        warn(f'[method status_code] {r.method} {response.status}')
        warn(f'[url] {response.url}')
        warn(f'[headers] {r.headers}')
        warn(f'[response body] {await response.text()[:200]}')

    async def getData(self, url, *args, **kwargs):
        """封装网络请求

        my_fmt:
            str: 默认项
                my_str_encoding
            json:
                my_json_encoding
                my_json_loads
            bytes:
                None
            streaming:
                my_streaming_chunk_size
                my_streaming_cb
        """
        resp, data, ok = None, None, False
        method = kwargs.pop('method', 'GET')
        str_encoding = kwargs.pop('my_str_encoding', None)
        fmt: Union[str, Generic[DataType]] = kwargs.pop('my_fmt', 'str')
        json_encoding = kwargs.pop('my_json_encoding', None)
        json_loads = kwargs.pop('my_json_loads', json.loads)
        streaming_chunk_size = kwargs.pop('my_streaming_chunk_size', 1024)
        streaming_cb = kwargs.pop('my_streaming_cb', None)
        max_try = kwargs.pop('my_retry', 1)

        for nr_try in range(max_try):
            try:
#-#                debug('url %s %s %s', url, pcformat(args), pcformat(kwargs))
                resp = await self.sess.request(method, url, *args, **kwargs)
                if fmt == 'str':
                    try:
                        data = await resp.text(encoding=str_encoding)
                    except UnicodeDecodeError:
                        txt = await resp.read()
                        data = txt.decode(str_encoding, 'ignore')
                        warn('ignore decode error from %s', url)
#-#                    except ContentEncodingError:
                    except aiohttp.client_exceptions.ContentTypeError:
                        warn('ignore content encoding error from %s', url)
                elif fmt == 'json':
                    data = await resp.json(encoding=json_encoding, loads=json_loads, content_type=None)
#-#                    if not data:
#-#                    if 'json' not in resp.headers.get('content-type', ''):
#-#                        warn('data not in json? %s', resp.headers.get('content-type', ''))
                elif fmt == 'bytes':
                    data = await resp.read()
                elif fmt == 'stream':
                    while 1:
                        chunk = await resp.content.read(streaming_chunk_size)
                        if not chunk:
                            break
                        streaming_cb(url, chunk)
                else:
                    data = await self._result(resp, fmt)
                ok = True
                break
#-#            except aiohttp.errors.ServerDisconnectedError:
#-#                debug('%sServerDisconnectedError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except asyncio.TimeoutError:
#-#                debug('%sTimeoutError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
                if nr_try == max_try - 1:  # 日志输出最后一次超时
                    debug('%sTimeoutError %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url)
            except aiohttp.client_exceptions.ClientConnectorError:
                debug('%sClientConnectionError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except ConnectionResetError:
                debug('%sConnectionResetError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except aiohttp.errors.ClientResponseError:
#-#                debug('%sClientResponseError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
#-#            except ClientHttpProcessingError:
#-#                debug('%sClientHttpProcessingError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
#-#            except ClientTimeoutError:
#-#                debug('%sClientTimeoutError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            except aiohttp.client_exceptions.ContentTypeError:
                debug('%sContentTypeError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
                data = await resp.text(encoding=str_encoding)
                info('data %s', data[:50])
            except ClientError:
                debug('%sClientError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
            except UnicodeDecodeError:
                debug('%sUnicodeDecodeError %s %s %s %s\n%s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), pcformat(resp.headers), await resp.read(), exc_info=True)
#-#                raise e
            except json.decoder.JSONDecodeError:
                debug('%sJSONDecodeError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs), exc_info=True)
            except aiodns.error.DNSError:
                debug('%sDNSError %s %s %s', ('%s/%s ' % (nr_try + 1, max_try)) if max_try > 1 else '', url, pcformat(args), pcformat(kwargs))
            finally:
                if resp:
                    resp.release()

        return resp, data, ok

    async def _result(self, response: aiohttp.ClientResponse,
                dcls: Generic[DataType] = None,
                status_code: Union[List, int] = 200) -> Union[Null, DataType]:
        """统一处理响应
        :param response:
        :param dcls:
        :param status_code:
        :return:
        """
        if isinstance(status_code, int):
            status_code = [status_code]
        if response.status in status_code:
            text = await response.text()
            if dcls is not None:
                if not text.startswith('{'):
                    return dcls()
                try:
                    # noinspection PyProtectedMember
                    return DataClass._fill_attrs(dcls, json.loads(text))
                except TypeError:
                    await self.debug_log(response)
                    error(dcls)
                    traceback.print_exc()

            return text

        warn(f'{response.status} {await response.text()[:200]}')
        return Null(response)

    async def clean(self):
        if self.sess:
            await self.sess.close()
            info('sess closed.')

if __name__ == '__main__':

    @dataclass
    class ResponseType:
        origin: str

    loop = asyncio.get_event_loop()

    try:
        net = NetManager(loop=loop)
        loop.run_until_complete(net())
        task = asyncio.ensure_future(net.getData('http://httpbin.org/ip', timeout=1, my_fmt=ResponseType))
        x = loop.run_until_complete(task)
        info(pcformat(x))

        task = asyncio.ensure_future(net.clean())
        x = loop.run_until_complete(task)
        info(pcformat(x))
    except KeyboardInterrupt:
        info('cancel on KeyboardInterrupt..')
        task.cancel()
        loop.run_forever()
        task.exception()
    finally:
        loop.stop()