from lxml.html import fromstring
import requests
import numpy as np
from itertools import cycle


def get_proxies(num=None):
    # url = 'https://free-proxy-list.net/'
    # response = requests.get(url)
    # parser = fromstring(response.text)
    # proxies = list(requests.get('https://proxy.rudnkh.me/txt').text.split())
    # for i in parser.xpath('//tbody/tr'):
    #     if i.xpath('.//td[7][contains(text(),"yes")]'):
    #         proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
    #         proxies.append(proxy)

    link = "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=1000&country=all&ssl=all&anonymity=all&uptime=100"
    proxies = list(requests.get(link).text.split())
    np.random.shuffle(proxies)
    proxies = []
    if len(proxies) == 0:
        proxies = list(requests.get(
            link[:-3]+'99').text.split())  # change uptime to 99
        np.random.shuffle(proxies)
    # print('Found', len(proxies), 'proxies, testing them now')

    if num is None:
        num = len(proxies)
    tested = test_proxies(proxies, num)
    return tested


def test_proxies(proxies, num):
    url = 'https://httpbin.org/ip'
    proxy_pool = cycle(proxies)
    working_proxies = []
    for i in range(1, len(proxies)):
        if num == 0:
            break
        # Get a proxy from the pool
        proxy = next(proxy_pool)
        # print("Request #%d" % i)
        try:
            response = requests.get(
                url, proxies={"http": proxy, "https": proxy}, timeout=1)
            # print(response.json())
            working_proxies.append(proxy)
            num -= 1
        except:
            # Most free proxies will often get connection errors. You will have retry the entire request using another proxy to work.
            # print("Skipping. Connnection error")
            pass
    return working_proxies


# proxies = get_proxies(5)
# # with open('proxies.txt') as f:
# #         proxies = f.read().splitlines()
# # test_proxies(proxies, 10)
# print(proxies)
