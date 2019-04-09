from lxml.html import fromstring
import requests
from itertools import cycle


def get_proxies():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr'):
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    
    tested = test_proxies(proxies)
    return tested


# proxies = get_proxies()
# proxy_pool = cycle(proxies)
# print(proxies)


def test_proxies(proxies):
    url = 'https://httpbin.org/ip'
    proxy_pool = cycle(proxies)
    working_proxies = set()
    count = 0
    for i in range(1, len(proxies)):
        count += 1
        if count == 10:
            break
        # Get a proxy from the pool
        proxy = next(proxy_pool)
        print("Request #%d" % i)
        try:
            response = requests.get(url, proxies = {"http": proxy, "https": proxy})
            print(response.json())
            working_proxies.add(proxy)
        except:
            # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
            # We will just skip retries as its beyond the scope of this tutorial and we are only downloading a single url
            print("Skipping. Connnection error")
    return working_proxies
