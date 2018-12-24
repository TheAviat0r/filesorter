import string
import random
import os
import sys
import logging
import configparser
import argparse

from tools import *

DEFAULT_CONFIG_FILE = 'configs/generator_config.cfg'


class FileGenerator(object):
    def __init__(self, config, chars=None):
        self.str_size = config.getint('string_size')
        self.batch_size = config.getint('batch_size')
        self.file_size = parse_memory(config.get('file_size'))
        self.output_path = config.get('output_path')
        if chars == None:
            self.chars = string.ascii_lowercase + string.digits

        logging.debug("Initialization of generator is finished")
        logging.debug(vars(self))

    def generate(self):
        logging.info("File generation has started")

        with open(self.output_path, 'w') as out_file:
            while True:
                if os.path.getsize(self.output_path) >= self.file_size:
                    break
                result_str = self._generate_batch(nrows=self.batch_size)
                out_file.write(result_str)

        logging.info("File '{}' has been generated".format(self.output_path))

    def _generate_batch(self, nrows=100):
        batch = [
            generate_string(self.chars, self.str_size) for _ in range(nrows)
        ]
        return "\n".join(batch) + "\n"


if __name__ == '__main__':
    setup_logger(level=logging.DEBUG)
    args = parse_arguments(DEFAULT_CONFIG_FILE)
    config = parse_config(args.config)
    if config == None:
        logging.error("Config file '{}' doesn't exist".format(config))
        logging.error("Exiting right now")
        sys.exit(1)

    file_generator = FileGenerator(config['FileGenerator'])
    file_generator.generate()
