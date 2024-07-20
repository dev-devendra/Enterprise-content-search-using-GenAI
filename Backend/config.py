import argparse
import logging
import sys

class config(object):
    def __init__(self):
        """
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("-i", "--input", help="Input csv file", required=True)
        arg_parser.add_argument("-r", "--run_id", help="Run identifier", required=True)
        arg_parser.add_argument("-l", "--loglevel", default=10, type=int,help="Log level [CRITICAL-50, ERROR-40, WARNING-30, INFO-20, DEBUG-10, NOTSET-0]")
        arg_parser.add_argument("-w", "--window_size", type=int,default=5, help="Data window size")
        arg_parser.add_argument("-t", "--training_split", type=float,default=0.8, help="Fraction of data for training")
        arg_parser.add_argument("-v", "--validation_split", type=float,default=0.1, help="Fraction of data for validation")
        arg_parser.add_argument("-d", "--dropout", default=0.2, type=float, help="Dropout value")
        arg_parser.add_argument("-b", "--log_dir", default=None, help="Log dir for TensorBoard use")
        arg_parser.add_argument("-e", "--epochs", default=500, type=int, help="Epoch count")
        arg_parser.add_argument("-n", "--node_count", default=100, type=int, help="GRU node count")
        arg_parser.add_argument("-k", "--kernel_count", default=32, type=int, help="CONV-2D kernel node count")
        arg_parser.add_argument("-z", "--batch_size", default=25, type=int, help="Batch size")
        arg_parser.add_argument("-f", "--stateful", action='store_true')
        arg_parser.add_argument("-o", "--optimizer", default="sgd",type=str, help='Optimizer')
        arg_parser.add_argument("-s", "--loss", default="mean_squared_error",type=str, help='Loss function')
        arg_parser.add_argument("-c", "--custom", default="", type=str, help='Parameter for custom program behavior')
        self.args = vars(arg_parser.parse_args())
        """
        self.create_logger()
        self.logger.debug("Logger created")
    
    def create_logger(self):
        self.logger = logging.getLogger('E/S')
        self.logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
