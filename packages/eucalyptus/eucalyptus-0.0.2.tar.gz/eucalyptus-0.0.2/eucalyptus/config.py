from configparser import ConfigParser
from pathlib import Path
import os

CONFIG_FILE_PATH = ".eucalyptus_config"


def check_config_file_exists():
    try:
        config = ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return os.path.exists(CONFIG_FILE_PATH)
    except Exception as e:
        return False


def set_default_config():
    exists = check_config_file_exists()
    if not exists:
        config = ConfigParser()
        if not config.has_section('api'):
            config.add_section('api')
        config.set('api', 'base_api_url', 'https://eucalyptus.ai/api')
        with open(CONFIG_FILE_PATH, 'w') as conf:
            config.write(conf)


def read_config():
    if not check_config_file_exists():
        set_default_config()
    config = ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config


def set_config_values(section, key, value):
    config = read_config()
    if section not in config.sections():
        config.add_section(section)
    config.set(section, key, value)
    with open(CONFIG_FILE_PATH, 'w') as conf:
        config.write(conf)


def set_api_token(api_token):
    try:
        set_config_values('api', 'api_token', api_token)
    except Exception as e:
        print(e)
        set_default_config()


def get_api_headers():
    config = read_config()
    try:
        api_token = config.get('api', 'api_token')
        headers = {'X-API-TOKEN': api_token}
        return headers
    except Exception as e:
        print(e)
        set_default_config()


def get_base_api_url():
    config = read_config()
    try:
        base_api_url = config.get('api', 'base_api_url')
        return base_api_url
    except Exception as e:
        print(e)
        set_default_config()


BASE_API_URL = get_base_api_url()
