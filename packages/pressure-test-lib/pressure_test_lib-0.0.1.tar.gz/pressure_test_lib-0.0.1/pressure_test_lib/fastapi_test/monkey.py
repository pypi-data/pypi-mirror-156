import json
import pytest
from pressure_test_lib.base.constants import PressureTestConfig
from pressure_test_lib.base.tools import get_mock_data
from pressure_test_lib.cache.cache import local_cache
from pressure_test_lib.fastapi_test.mock_data import init_cache_mock_data

try:
    import aiohttp
except ImportError:
    pass
else:
    _client_session_request = aiohttp.ClientSession._request
    from aiohttp.client_reqrep import ClientResponse
    from aiohttp import http
    from multidict import CIMultiDict, CIMultiDictProxy
    from aiohttp import RequestInfo
    from unittest import mock
    from aiohttp.helpers import TimerNoop
    from yarl import URL
    import asyncio


@pytest.fixture
def session():
    return mock.Mock()


def mock_response(method, mock_data):
    """mock一个response对象"""
    headers = CIMultiDict()
    headers['Content-Type'] = 'application/json'
    headers = CIMultiDictProxy(headers)
    request_info = RequestInfo('http://pressure_test', "get", headers, 'http://pressure_test')
    loop = asyncio.get_event_loop()
    response = ClientResponse(
        method,
        URL("http://pressure_test"),
        request_info=request_info,
        writer=mock.Mock(),
        continue100=None,
        timer=TimerNoop(),
        traces=[],
        loop=loop,
        session=session,
    )

    def side_effect():
        fut = loop.create_future()
        fut.set_result(mock_data.encode("utf-8"))
        return fut

    response._headers = {"Content-Type": "application/json"}
    content = response.content = mock.Mock()
    content.read.side_effect = side_effect
    response.status = 200
    return response


async def client_session_request_wrapper(*args, **kwargs):
    """Wraps aiohttp.ClientSession._request"""
    if PressureTestConfig.switch:
        # 压测配置是否开启，用来判断是否为压测命名空间
        mock_data_cache = local_cache.get(PressureTestConfig.mock_cache_key)
        if mock_data_cache:
            # 从内存获取mock数据，内存中没有直接发起真实请求，内存里存的mock数据结构 {'data':{'domain_name_uri':mock_data}}
            if local_cache.is_expired(mock_data_cache):
                # 如果内存数据过期，则再从redis取数据存进内存
                mock_data_cache = await init_cache_mock_data()
            method, url = args[1], args[2]
            mock_data = get_mock_data(mock_data_cache, url)
            if mock_data:
                # 如果内存中没数据就直接发起请求
                return mock_response(method, mock_data)

    response = await _client_session_request(*args, **kwargs)
    return response


def patch_requests():
    if '_client_session_request' not in globals():
        raise Exception("aiohttp not installed.")
    aiohttp.ClientSession._request = client_session_request_wrapper
