import os
import time
import random
import json
import logging
import requests
import conf
import utils

with open('config.json', 'r', encoding='utf-8') as config_f:
    config_dict = json.load(config_f)
conf.parse(config_dict)

os.chdir(conf.work_path)
indexes = utils.Index('index.json')

touched = 0
succ_download = 0
fail_download = 0
need_download = []
for entity in indexes.index:
    path = entity.ensure_path()
    if os.path.exists(path):
        utils.info('图片{}已存在'.format(path))
        touched += 1
    else:
        utils.info('图片{}不存在，准备下载'.format(path))
        need_download.append((entity, path))

sess = requests.Session()
sess.proxies = conf.proxies
sess.headers.update({
    'user-agent': conf.ua,
    'cookie': conf.cookie_string,
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'origin': 'https://www.fanbox.cc'
})
for i, (entity, path) in enumerate(need_download):
    if i > 0:
        time.sleep(conf.wait_sec + random.randint(5, 15))
    try:
        utils.info('图片{}下载中'.format(path))
        res = sess.get(entity.image_url, headers={'referer': entity.page_url})
        if res.ok:
            with open(path, 'wb') as target:
                target.write(res.content)
            succ_download += 1
            utils.info('已成功下载')
        else:
            fail_download += 1
            utils.warning('请求失败')
    except:
        fail_download += 1
        utils.warning('请求异常')
print('成功下载了{}张新图片，失败{}张，{}张图片已存在'.format(succ_download, fail_download, touched))
