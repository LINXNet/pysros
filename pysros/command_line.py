# Copyright (c) 2021 London Internet Exchange Ltd.

import argparse
import logging
import sys
import textwrap
import time

import napalm   # pylint: disable=import-error
import yaml     # pylint: disable=import-error


def time_func(func):
    """ Decorator adding the execution time for the decorated function """
    def wrapper():
        t1 = time.time()
        func()
        t2 = time.time()
        print(f'Function: "{func.__name__}", completed in: "{t2 - t1}" s')
    return wrapper


def parse_and_get_args():
    """
    Create arg parser.
    Returns: argparse.ArgumentParser

    """
    parser = argparse.ArgumentParser(
        description='Diff and Replace/Merge configs.',
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        'config_file_path',
        help='Config file with user details like username and password',
    )

    parser.add_argument(
        'hostname',
        help='Hostname of the switch',
    )

    parser.add_argument(
        'action',
        choices=[
          'diff',
          'replace',
          'merge',
          'running'
        ],
        help=textwrap.dedent("""
          Please choose one action from below
          'diff' Compare Running config with Candidate config.
          'replace' Replace Running config with Candidate config.
          'merge' Merge Candidate config with Running config.
          'running' Get running config from switch and save it to a file.

          """),
    )

    parser.add_argument(
        '-s',
        '--save-config-file-path',
        dest='save_config_file_path',
        default="running.conf",
        help=textwrap.dedent("""
          File path to save running config in.
          If no path is given than file will be saved in current dir
          with hostname-action.xml. For example for running config with
          hostname foo.bar foo.bar-running.xml will be created.

          """)
    )

    parser.add_argument(
        '-f',
        '--format',
        dest='format',
        choices=["xml", "cli"],
        default="xml",
        help=textwrap.dedent("""
        The format in which interact with the Nokia device.
        If using a payload its format will overwrite this option.

        """)
    )

    parser.add_argument(
        '-c',
        '--candidate-file-path',
        dest='candidate_file_path',
        help='Candidate file path',
    )

    parser.add_argument(
        '-v',
        '--verbosity',
        action='count',
        default=0,
        dest='verbosity',
        help=textwrap.dedent("""
          Set logging verbose level. It accepts a number >= 0.
          The default value is 0,
          the minimal log besides stack backtrace is given;
          Verbose level 1 enables debug level logging for pysros;
          Verbose level 2 emits ncclient debug level logging as well.

          """)
    )

    args = parser.parse_args()
    if args.action in ['diff', 'replace', 'merge'] and not \
            args.candidate_file_path:
        parser.error(
            "diff, replace and merge action requires -c,"
            " --candidate-file-path."
        )
    elif args.action == "running" and args.candidate_file_path:
        parser.error(
            '\nERROR: action: "running" and option: '
            '"-c, --candidate-file-path" cannot be specified together\n'
        )
    return args


@time_func
def main():
    """ Main function """
    # pylint: disable=too-many-locals
    args = parse_and_get_args()
    config_path = args.config_file_path
    switch_name = args.hostname
    operation = args.action
    running_conf_path = args.save_config_file_path
    candidate_conf_path = args.candidate_file_path
    verbosity = args.verbosity
    config_format = args.format

    with open(config_path, encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)['config']

    driver = napalm.get_network_driver('sros')
    with driver(hostname=switch_name,
                username=config['username'],
                timeout=180,
                optional_args={'sros_get_format': config_format,
                               'sros_compare_format': 'json'},
                password=config['password']) as device:
        if verbosity:
            console_handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(name)s | %(levelname)s |'
                ' %(filename)s/%(funcName)s:%(lineno)d | %(message)s'
            )
            console_handler.setFormatter(formatter)
            logging.getLogger('ncclient').addHandler(console_handler)

            if int(verbosity) == 1:
                logging.getLogger('ncclient').setLevel(logging.ERROR)
            elif int(verbosity) == 2:
                logging.getLogger('ncclient').setLevel(logging.INFO)
            else:
                logging.getLogger('ncclient').setLevel(logging.DEBUG)

        if operation == 'running':
            # pylint: disable=unexpected-keyword-arg
            result = device.get_config(retrieve='running')
            with open(running_conf_path, 'w', encoding='utf-8') as running:
                running.write(result['running'])

        elif operation == 'merge':
            device.load_merge_candidate(filename=candidate_conf_path)
            device.commit_config()

        elif operation == 'replace':
            device.load_replace_candidate(filename=candidate_conf_path)
            device.commit_config()

        elif operation == 'diff':
            device.load_replace_candidate(filename=candidate_conf_path)
            # pylint: disable=unexpected-keyword-arg
            print(device.compare_config())


if __name__ == '__main__':
    main()
