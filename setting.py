import yaml
import os

ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
CONFIG_FILE = os.path.join(ROOT_DIR, 'config.yml')


def load_settings():
    with open(CONFIG_FILE, 'r') as ymlfile:
        return yaml.load(ymlfile)


def save_settings():
    with open(CONFIG_FILE, 'w') as ymlfile:
        yaml.dump(config, ymlfile, default_flow_style=False)


config = load_settings()
