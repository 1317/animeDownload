import requests
from bs4 import BeautifulSoup

import re
from datetime import datetime, timezone, timedelta

proxies = {'http': 'socks5://127.0.0.1:10888', 'https': 'socks5://127.0.0.1:10888'}
proxy = '127.0.0.1:10888'

def getLinkfromVCBS(link):
    r = requests.get(link, proxies=proxies)
    s = BeautifulSoup(r.text, 'html.parser')
    title = s.title.string.replace('\n', '')
    try:
        chineseTitle = re.match(r'.*10....', title).group().split('/')[1][1:-6].replace(' 10-bit', '')
    except:
        chineseTitle = '无'
    nyaaLink = ''.join(s.find_all('a', text=re.compile('nyaa\.si'))[0])
    print('获取Nyaa链接成功', end='\t...\t')
    return nyaaLink, chineseTitle


def analysisNyaaPage(link):
    r = requests.get(link, proxies=proxies)
    info = {}
    s = BeautifulSoup(r.text, 'html.parser')
    title = s.title.string.replace('\n', '')

    info['author'] = re.match(r'[\[【].+?[\]】]', title).group()
    info['title'] = title.replace(info['author'], '').replace(' :: Nyaa', '')[1:]
    info['EnglishTitle'] = title.replace(info['author'], '').replace(' :: Nyaa', '')[1:].split('/')[0]
    info['author'] = info['author'][1:-1]

    tags = [r'Date', r'File size', r'Info hash']

    for tag in tags:
        for i in s.find_all('div', text=re.compile(tag)):
            info[tag] = i.next_sibling.next_sibling.string.replace('&amp;', '&')

    # 文件大小单位转换
    try:
        if 'GiB' in info['File size']:
            info['File size'] = float(info['File size'].replace(' GiB'))
        elif 'MiB' in info['File size']:
            info['File size'] = float(info['File size'].replace(' MiB')) / 1024
    except:
        info['File size'] = re.match(r"[0-9\.]*", info['File size']).group()

    # 切换时区
    timeZoneChina = timezone(timedelta(hours=8))
    dt = datetime.strptime(info['Date'], '%Y-%m-%d %H:%M UTC').replace(tzinfo=timezone.utc)
    info['Date'] = dt.astimezone(timeZoneChina).strftime('%Y-%m-%d %H:%M:%S')

    for i in s.find_all(text=re.compile(r'Magnet')):
        info['MagLink'] = i.parent['href'].replace('&amp;', '&')

    return info