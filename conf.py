import os

class ConfigError(Exception):
    pass

def check_str_list(l):
    if not isinstance(l, list):
        return False
    for item in l:
        if not isinstance(item, str):
            return False
    return True

def parse(config_dict):
    global work_path, proxies, ua, creators, wait_sec, cookie_string
    work_path = config_dict['work-path']
    if not os.path.isdir(work_path):
        raise ConfigError('work-path="{}" 不是一个合法的路径'.format(work_path))
    proxies = dict()
    if 'proxy' in config_dict:
        proxies['http'] = config_dict['proxy']
        proxies['https'] = config_dict['proxy']
    ua = config_dict['user-agent']
    if not isinstance(ua, str):
        raise ConfigError('user-agent="{}" 不是字符串'.format(ua))
    creators = config_dict['illustrator']
    if not check_str_list(creators):
        raise ConfigError('illustrator 不是字符串列表')
    wait_sec = config_dict['wait-sec']
    if not (isinstance(wait_sec, int) and wait_sec > 0):
        raise ConfigError('wait-sec="{}" 不是正整数'.format(wait_sec))
    if 'cookie-string' in config_dict:
        cookie_string = config_dict['cookie-string']
        if not isinstance(cookie_string, str):
            raise ConfigError('cookie-string="{}" 不是字符串'.format(cookie_string))
    else:
        cookie_string = input('Cookie:')
