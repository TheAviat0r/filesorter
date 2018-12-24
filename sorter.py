import argparse
import configparser
import os
import sys
import heapq

from tools import *

class FileSorter(object):
    def __init__(self, config):
        assert config

        self.config = config
        self.memory_limit = parse_memory(config.get("memory_limit"))
        self.input_path = config.get("input_path")
        self.output_path = config.get("output_path")
        self.work_directory_path = config.get("work_directory_path")

        logging.debug("FileSorter initialized:")
        logging.debug(vars(self))

    def configure(self):
        assert self.work_directory_path

        if not os.path.exists(self.work_directory_path):
            logging.info("Creating new empty work directory:")
            logging.info("Path: {}".format(self.work_directory_path))
            os.makedirs(self.work_directory_path)
            return

        logging.info("Working directory exists. Emptying it")

        for f in os.listdir(self.work_directory_path):
            old_file = os.path.join(self.work_directory_path, f)
            logging.debug("Removing {}".format(old_file))
            os.remove(old_file)

    def sort(self):
        if not os.path.exists(self.input_path):
            raise IOError("Input file {} doesn't exist".format(self.input_path))

        if os.path.getsize(self.input_path) < self.memory_limit:
            logging.debug("Optimization - in-memory sorting is possible")
            logging.info("Starting sorting {}".format(self.input_path))

            input_file = open(self.input_path)
            output_file = open(self.output_path, 'w')
            lines = input_file.readlines()
            lines.sort()
            output_file.writelines(lines)

            return

        self.configure()

        logging.info("Starting external sorting {}".format(self.input_path))

        logging.info("Splitting {} into sorted chunks".format(self.input_path))
        splitter = FileSplitter(self.input_path, self.memory_limit,
                                self.work_directory_path)
        splitter.split()

        logging.info("Merging chunks at {}".format(self.work_directory_path))
        merger = FileMerger(self.work_directory_path,
                            self.output_path)
        merger.merge()

        clean_directory(self.work_directory_path)

        logging.info("{} is sorted".format(self.input_path))
        logging.info("Output at {}".format(self.output_path))


class FileMerger(object):
    def __init__(self, work_dir, output_path):
        self.work_dir = work_dir
        self.output_path = output_path
        
        self.temp_files = os.listdir(self.work_dir)
        self.temp_files = [os.path.join(work_dir, f) for f in self.temp_files]

        logging.debug("FileMerger initialized:")
        logging.debug(vars(self))

    def merge(self):
        logging.debug("Merging files: {}".format(self.temp_files))

        temp_files = []
        try:
            for f in self.temp_files:
                temp_files.append(open(f))

            output_file = open(self.output_path, 'w')

            output_file.writelines(heapq.merge(*temp_files))
        finally:
            for f in temp_files:
                f.close()
            output_file.close()


class FileSplitter(object):
    def __init__(self, file_name, batch_size, temp_dir):
        self.file_name = file_name
        self.batch_size = batch_size
        self.temp_dir = temp_dir
        self.template = "part-{}.txt"

        logging.debug("FileSplitter initialized:")
        logging.debug(vars(self))

    def split(self):
        with open(self.file_name) as input_file:
            batch_num = 1
            batch_lines = []

            while True:
                batch_lines = input_file.readlines(self.batch_size)
                if batch_lines == []:
                    break

                batch_lines.sort()

                fname = self._write_batch(batch_lines, batch_num)
                batch_num += 1

    def _write_batch(self, batch_lines, batch_num):
        logging.debug("Writing batch {}".format(batch_num))

        temp_fname = self.template.format(batch_num)
        temp_fname = os.path.join(self.temp_dir, temp_fname)

        logging.debug("Path: {}".format(temp_fname))

        temp_file = open(temp_fname, 'w')
        temp_file.writelines(batch_lines)
        temp_file.close()

        return temp_fname


def setup_logger(level=logging.DEBUG, output=sys.stdout):
    logger = logging.getLogger()
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    format_str = '[%(asctime)s] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)

    logger.addHandler(handler)

if __name__ == '__main__':
    setup_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("-m",
                        "--mem",
                        default="100M",
                        help="Memory limit used for sorting")
    parser.add_argument("-c",
                        "--config",
                        default="configs/sorter_config.cfg",
                        help="Path to app config file")
    parser.add_argument("-f",
                        "--file",
                        default=None,
                        help="Path to input file")
    parser.add_argument("-o",
                        "--output",
                        default=None,
                        help="Path to output file")
    args = parser.parse_args() 

    if not os.path.exists(args.config):
        logging.debug("Config at path '{}' doesn't exists".format(config_path))
        logging.debug("Exiting right now")
        sys.exit(1)

    config_file = open(args.config, 'r')
    config = configparser.ConfigParser()
    config.read_file(config_file)
    
    if args.mem != "100M":
        config.set("FileSorter", "memory_limit", args.mem)
    if args.file != None:
        config.set("FileSorter", "input_path", args.file)
    if args.output != None:
        config.set("FileSorter", "output_path", args.output)

    try:
        sorter = FileSorter(config['FileSorter'])
        sorter.sort()
    except Exception as e:
        logging.info(str(e))
