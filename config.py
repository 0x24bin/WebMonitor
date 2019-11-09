# -*- coding: utf-8 -*-

"""
    config
    ~~~~~~

    Implements configuration


"""

import sys
import traceback
import configparser
import os
import json
from log import logger


#conf_name = sys.argv[1] if len(sys.argv) == 2 else 'config.ini'
#上层目录
#project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
#当前目录
project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__)))
config_path = os.path.join(project_directory, 'config.ini')
rules_path = os.path.join(project_directory, 'rule.json')
#print(config_path)




def get(level1=None, level2=None):
    """
    Get config value
    :param level1:
    :param level2:
    :return: string
    """
    if level1 is None and level2 is None:
        return
    config = configparser.ConfigParser()

    config.read(config_path)
    value = None
    try:
        value = config.get(level1, level2)
        #print (value)
    except Exception as e:
        print(level1, level2)
        traceback.print_exc()
        print("config.ini file configure failed.\nError: {0}".format(e))
    return value

# Rules Structure Design
#
# 'rule keywords': {
#     'mode': '' // RuleMode: normal-match(default)/only-match/full-match/mail
#     'extension': '' // search extension: (default)/txt/md/java/python/etc...
# }
#
try:
    with open(rules_path) as f:
        rules_dict = json.load(f)
except Exception as e:
    logger.critical('please config rules.json!')
    logger.critical(traceback.format_exc())

#print(rules_dict.items())

class Rule(object):
    def __init__(self, types=None,url=None,mode=None):
        self.types = types
        self.url = url
        #self.filename = url.replace("/","-")
        self.mode = mode

# 读取配置文件
def get_rules(rule_type='singlepage'):
    rules_objects = []
    for types, rule_list in rules_dict.items():
        if types in rule_type:
            types =types.upper()
            for url,rule_attr in rule_list.items():
                if 'mode' in rule_attr:
                    mode = rule_attr['mode']
                else:
                    mode = None
                r = Rule(types,url,mode)
                #print(url,types,mode)
                rules_objects.append(r)
    return rules_objects




if __name__ == '__main__':
    #print(get('mail', 'host'))
    rules = get_rules()
    if len(rules) == 0:
        print('aaa')
    for idx,rule_object in enumerate(rules):
        print(idx,rule_object.url)

