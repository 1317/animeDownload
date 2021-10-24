import re
from datetime import datetime, timezone, timedelta

import requests
from bs4 import BeautifulSoup

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

    info['author'] = re.match(r'\[.+?\]', title).group()
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


def getWorkInfo(link):
    info = {}
    try:
        if 'vcb-s' in link:
            print(f'VCB-Studio 链接 {link}', end='\t...\t')
            nyaaLink, chineseTitle = getLinkfromVCBS(link)
        elif 'nyaa' in link:
            print(f'Nyaa 链接 {link}', end='\t...\t')
            chineseTitle = '无'
            nyaaLink = link
        else:
            print(f'无法识别的链接：{link}')
            raise ValueError

        info = analysisNyaaPage(nyaaLink)
        if chineseTitle:
            info['ChineseTitle'] = chineseTitle
        else:
            info['ChineseTitle'] = '无'
        info['status'] = True
        print('信息获取成功')
    except:
        info['status'] = False
        print('\t信息获取失败')

    return info


linkList = []
print('Link?')
while True:
    link = input('')
    if link != '':
        linkList.append(link)
    else:
        break

# linkList = ['0','https://vcb-s.com/archives/13633', 'https://nyaa.si/view/1332385', '111']

print('输入{}个链接，开始获取信息……\n'.format(len(linkList)))

infoList = []
count = 1
total = len(linkList)
failedLinks = []
for link in linkList:
    print(f'[{count}/{total}]\t', end='')
    info = getWorkInfo(link)
    if info['status']:
        infoList.append(info)
    else:
        failedLinks.append(link)
    count += 1

print(f'读取了{total}个链接\t{len(infoList)}个成功')
if len(failedLinks):
    print(f'\t{len(failedLinks)}个失败:', '\n\t'.join(failedLinks))

resultFileName = f'result_{int(datetime.now().timestamp())}.txt'
with open(resultFileName, 'w', encoding='utf-8') as result:
    result.write('-' * 20 + '番剧信息' + '-' * 20 + '\n')
    for info in infoList:
        result.write('{title}\t{size}\t{date}\t{author}\t{hash}\n'.format(title=info['title'],
                                                                          size=info['File size'],
                                                                          date=info['Date'],
                                                                          author=info['author'],
                                                                          hash=info['Info hash']))
    result.write('-' * 20 + '中英标题' + '-' * 20 + '\n')
    for info in infoList:
        result.write(f"{info['ChineseTitle']}\t{info['EnglishTitle']}\n")
    result.write('-' * 20 + '磁力链接' + '-' * 20 + '\n')
    for info in infoList:
        result.write('{magnet}\n'.format(magnet=info['MagLink']))
    result.write('-' * 20 + '失败链接' + '-' * 20 + '\n')
    for flink in failedLinks:
        result.write(f'{flink}\n')
    print(f'\n结果保存为{resultFileName}')
