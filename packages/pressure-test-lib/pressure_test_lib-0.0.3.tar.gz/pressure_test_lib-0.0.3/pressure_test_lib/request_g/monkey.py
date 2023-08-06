from pressure_test_lib.base.constants import PressureTestConfig
from pressure_test_lib.cache.cache import local_cache
from pressure_test_lib.request_g.mock_data import init_cache_mock_data
from pressure_test_lib.base.tools import get_mock_data

try:
    import requests.adapters
except ImportError:
    pass
else:
    _HTTPAdapter_send = requests.adapters.HTTPAdapter.send
    from requests import Response


def mock_response(mock_data):
    """mock一个response对象"""
    response = Response()
    response.status_code = 200
    response._content = bytes(mock_data, 'utf-8')
    response.headers = 'application/json'
    return response


def requests_send_wrapper(http_adapter, request, **kwargs):
    """Wraps HTTPAdapter.send"""
    if PressureTestConfig.switch:
        # 压测配置是否开启，用来判断是否为压测命名空间
        mock_data_cache = local_cache.get(PressureTestConfig.mock_cache_key)
        if local_cache.is_expired(mock_data_cache):
            # 如果内存数据过期，则再从redis取数据存进内存
            mock_data_cache = init_cache_mock_data()
        method, url = request.method, request.url
        mock_data = get_mock_data(mock_data_cache, url)
        if mock_data:
            return mock_response(mock_data)

    response = _HTTPAdapter_send(http_adapter, request, **kwargs)
    return response


def patch_requests():
    if '_HTTPAdapter_send' not in globals():
        raise Exception("requests not installed.")
    requests.adapters.HTTPAdapter.send = requests_send_wrapper
