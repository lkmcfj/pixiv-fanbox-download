import os
import queue
import json
import time
import random
import logging
import requests
import utils
import conf


def process_list(creator, list_api):
    global request_queue, cur_indexes, skipped_post
    utils.info('creator {} - processing list: {}'.format(creator, list_api))
    headers = {'referer': utils.list_page(creator)}
    res = sess.get(list_api, headers=headers)
    if res.ok:
        json_res = res.json()
        if 'body' in json_res:
            if ('nextUrl' in json_res['body']) and json_res['body']['nextUrl']:
                request_queue.put((process_list, [creator, json_res['body']['nextUrl']]))
            if 'items' in json_res['body']:
                for item in json_res['body']['items']:
                    if item['restrictedFor']:
                        utils.info('post {} of creator {} is restricted'.format(item['id'], creator))
                    else:
                        if item['id'] in cur_indexes.post_set:
                            skipped_post += 1
                            utils.info('post {} of creator {} has been recorded, skipped'.format(item['id'], creator))
                        else:
                            utils.info('post {} of creator {} found'.format(item['id'], creator))
                            request_queue.put((process_post, [creator, item['id']]))
            else:
                utils.warning('key "items" not found'.format(creator))
        else:
            utils.error('key "body" not found')
    else:
        utils.error('request failed')

def process_post(creator, post_id):
    global cur_indexes, new_image
    utils.info('process post {} of creator {}'.format(post_id, creator))
    page_url = utils.post_page(creator, post_id)
    headers = {'referer': page_url}
    res = sess.get(utils.post_page_api(post_id), headers=headers)
    if res.ok:
        json_res = res.json()
        if ('body' in json_res) and ('body' in json_res['body']):
            title = json_res['body']['title']
            if ('images' in json_res['body']['body']) and (len(json_res['body']['body']['images']) > 0):
                for image in json_res['body']['body']['images']:
                    cur_entity = utils.Entity(creator, post_id, page_url, image['originalUrl'], image['id'] + '.' + image['extension'], title)
                    if cur_indexes.add(cur_entity):
                        utils.info('new image {} found'.format(cur_entity.image_filename))
                        new_image += 1
            else:
                utils.warning('no image found')
        else:
            utils.error('key "body" not found')
    else:
        utils.error('request failed')

with open('config.json', 'r', encoding='utf-8') as config_f:
    config_dict = json.load(config_f)
conf.parse(config_dict)

os.chdir(conf.work_path)
sess = requests.Session()
sess.proxies = conf.proxies
sess.headers.update({
    'user-agent': conf.ua,
    'cookie': conf.cookie_string,
    'accept': 'application/json',
    'origin': 'https://www.fanbox.cc'
})

cur_indexes = utils.Index('index.json')
request_queue = queue.SimpleQueue()
skipped_post = 0
new_image = 0
for creator in conf.creators:
    request_queue.put((process_list, [creator, utils.start_list_api(creator)]))
while not request_queue.empty():
    cur_func, cur_arg = request_queue.get()
    cur_func(*cur_arg)
    if not request_queue.empty():
        time.sleep(conf.wait_sec + random.randint(5, 15))
print('完成索引! 找到了{}个新图片，跳过了{}个已索引页面'.format(new_image, skipped_post))

