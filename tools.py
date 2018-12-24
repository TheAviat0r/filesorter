import os
import sys
import logging
import random
import argparse
import configparser


def setup_logger(level=logging.INFO, output=sys.stdout):
    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    format_str = '[%(asctime)s] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)

    logger.addHandler(handler)


def clean_directory(path):
    logging.info("Cleaning directory {}".format(path))

    for f in os.listdir(path):
        f_path = os.path.join(self.work_directory_path, f)
        logging.debug("Removing {}".format(f_path))
        os.remove(f_path)


def parse_arguments(default_config_path):
    parser = argparse.ArgumentParser(description='Process file generator args')
    parser.add_argument(
        '-c', '--config',
        help='Path to config file',
        default=default_config_path
    )

    args = parser.parse_args()

    return args


def parse_memory(string):
    if string[-1].lower() == 'k':
        return int(string[:-1]) * 1024
    elif string[-1].lower() == 'm':
        return int(string[:-1]) * 1024 * 1024
    elif string[-1].lower() == 'g':
        return int(string[:-1]) * 1024 * 1024 * 1024

    return int(string[:-1])


def clean_directory(path):
    assert path
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))


def generate_string(charset, string_size):
    return ''.join(random.choice(charset) for _ in range(string_size)) + "\n"


def parse_config(config_path):
    if not os.path.exists(config_path):
        return None

    config_file = open(config_path)
    config = configparser.ConfigParser()
    config.read_file(config_file)

    return config
