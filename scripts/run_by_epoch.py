from argparse import ArgumentParser
from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from signal import SIGUSR1, SIGUSR2, signal
from subprocess import PIPE, run
from sys import exit, stdout


def get_command_line_arguments():
    parser = ArgumentParser()
    parser.add_argument('Animal', type=str, help='Short name of animal')
    parser.add_argument('Day', type=int, help='Day of recording session')
    parser.add_argument('Epoch', type=int,
                        help='Epoch number of recording session')
    parser.add_argument(
        '-d', '--debug',
        help='More verbose output for debugging',
        action='store_const',
        dest='log_level',
        const=DEBUG,
        default=INFO,
    )
    return parser.parse_args()


def get_logger():
    formatter = Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler = StreamHandler(stream=stdout)
    handler.setFormatter(formatter)
    logger = getLogger()
    logger.addHandler(handler)
    return logger


def main():
    args = get_command_line_arguments()
    logger = get_logger()
    logger.setLevel(args.log_level)

    def _signal_handler(signal_code, frame):
        logger.error('***Process killed with signal {signal}***'.format(
            signal=signal_code))
        exit()

    for code in [SIGUSR1, SIGUSR2]:
        signal(code, _signal_handler)

    epoch_key = (args.Animal, args.Day, args.Epoch)
    logger.info(
        'Processing epoch: Animal {0}, Day {1}, Epoch #{2}...'.format(
            *epoch_key))
    git_hash = run(['git', 'rev-parse', 'HEAD'],
                   stdout=PIPE, universal_newlines=True).stdout
    logger.info('Git Hash: {git_hash}'.format(git_hash=git_hash.rstrip()))

    logger.info('Finished Processing')


if __name__ == '__main__':
    exit(main())
