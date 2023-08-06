from urllib.parse import urlparse

from pressure_test_lib.base.constants import PressureTestConfig


def url_to_domain_path(url):
    """从url获取域名和uri"""
    url = urlparse(url)
    domain = url.hostname
    path = url.path
    return domain, path


def get_mock_data(mock_data_cache, url):
    """获取mock数据"""
    data = mock_data_cache.get('data', {})
    domain_name, uri = url_to_domain_path(url)
    mock_data = data.get('%s%s' % (domain_name, uri))
    return mock_data
