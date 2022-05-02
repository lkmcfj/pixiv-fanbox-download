import os
import json
import logging

class Entity:
    
    def __init__(self, creator, post_id, page_url, image_url, image_filename, title):
        self.creator = creator
        self.post_id = post_id
        self.page_url = page_url
        self.image_url = image_url
        self.image_filename = image_filename
        self.title = title
    
    @classmethod
    def from_dict(cls, info_dict):
        return cls(info_dict['creator'], info_dict['post_id'], info_dict['page_url'], info_dict['image_url'], info_dict['image_filename'], info_dict['title'])
    
    def ensure_path(self):
        if not os.path.isdir(self.creator):
            os.mkdir(self.creator)
        res_path = self.creator
        title_path = os.path.join(self.creator, self.title.strip('. '))
        id_path = os.path.join(self.creator, self.post_id)
        if os.path.isdir(title_path):
            res_path = title_path
        elif os.path.isdir(id_path):
            res_path = id_path
        else:
            try:
                os.mkdir(title_path)
                res_path = title_path
            except:
                os.mkdir(id_path)
                res_path = id_path
        return os.path.join(res_path, self.image_filename)
    
    def __eq__(self, other):
        return (self.creator == other.creator) and (self.post_id == other.post_id) \
            and (self.page_url == other.page_url) and (self.image_url == other.image_url) \
            and (self.image_filename == other.image_filename) and (self.title == other.title)

class Index:

    def __init__(self, filename):
        self.filename = filename
        if os.path.isfile(filename):
            with open(filename, 'r', encoding='utf-8') as index_f:
                raw_list = json.load(index_f)
            self.index = [Entity.from_dict(entity_dict) for entity_dict in raw_list]
        else:
            self.index = []
            with open(filename, 'w', encoding='utf-8') as index_f:
                json.dump(self.index, index_f)
        self.post_set = set()
        for entity in self.index:
            self.post_set.add(entity.post_id)

    def add(self, entity):
        for exist_entity in self.index:
            if exist_entity == entity:
                return False
        self.index.append(entity)
        self.post_set.add(entity.post_id)
        self.update()
        return True
    
    def update(self):
        dump_list = [entity.__dict__ for entity in self.index]
        with open(self.filename, 'w', encoding='utf-8') as index_f:
            json.dump(dump_list, index_f, indent=4)

def start_list_api(creator):
    return 'https://api.fanbox.cc/post.listCreator?creatorId={}&limit=10'.format(creator)

def list_page(creator):
    return 'https://www.fanbox.cc/@{}'.format(creator)

def post_page(creator, post_id):
    return 'https://www.fanbox.cc/@{}/posts/{}'.format(creator, post_id)

def post_page_api(post_id):
    return 'https://api.fanbox.cc/post.info?postId={}'.format(post_id)

logging.basicConfig(format='%(message)s', level=logging.INFO)
def info(message):
    logging.info(message)
def warning(message):
    logging.warning('\033[33m' + message + '\033[0m')
def error(message):
    logging.error('\033[31m' + message + '\033[0m')