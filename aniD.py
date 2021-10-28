import os
from datetime import datetime

import sites

def getWorkInfo(link):
    info = {}
    try:
        if 'vcb-s' in link:
            print(f'VCB-Studio 链接 {link}', end='\t...\t')
            nyaaLink, chineseTitle = sites.getLinkfromVCBS(link)
        elif 'nyaa' in link:
            print(f'Nyaa 链接 {link}', end='\t...\t')
            chineseTitle = '无'
            nyaaLink = link
        else:
            print(f'无法识别的链接：{link}')
            raise ValueError

        info = sites.analysisNyaaPage(nyaaLink)
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
with open(os.path.join(os.getcwd(),'results',resultFileName), 'w', encoding='utf-8') as result:
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
