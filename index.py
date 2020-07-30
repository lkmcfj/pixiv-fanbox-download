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
    global request_queue
    logging.info('creator {} - processing list: {}'.format(creator, list_api))
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
                        logging.info('post {} of creator {} is restricted'.format(item['id'], creator))
                    else:
                        logging.info('post {} of creator {} found'.format(item['id'], creator))
                        request_queue.put((process_post, [creator, item['id']]))
            else:
                logging.warning('key "items" not found'.format(creator))
        else:
            logging.warning('key "body" not found')
    else:
        logging.error('request failed')

def process_post(creator, post_id):
    global cur_indexes
    logging.info('process post {} of creator {}'.format(post_id, creator))
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
                    logging.info('image {} touched'.format(cur_entity.image_filename))
                    cur_indexes.add(cur_entity)
            else:
                logging.warning('no image found')
        else:
            logging.warning('key "body" not found')
    else:
        logging.error('request failed')

logging.basicConfig(format='%(message)s', level=logging.INFO)
with open('config.json', 'r', encoding='utf-8') as config_f:
    config_dict = json.load(config_f)
conf.parse(config_dict)

os.chdir(conf.work_path)
cur_indexes = utils.Index('index.json')
sess = requests.Session()
sess.proxies = conf.proxies
sess.headers.update({
    'user-agent': conf.ua,
    'cookie': conf.cookie_string,
    'accept': 'application/json',
    'origin': 'https://www.fanbox.cc'
})

request_queue = queue.SimpleQueue()
for creator in conf.creators:
    request_queue.put((process_list, [creator, utils.start_list_api(creator)]))
while not request_queue.empty():
    cur_func, cur_arg = request_queue.get()
    cur_func(*cur_arg)
    if not request_queue.empty():
        time.sleep(conf.wait_sec + random.randint(5, 15))
print('完成索引! 找到了{}个新图片和{}个已有图片'.format(cur_indexes.found_new, cur_indexes.touch_old))

