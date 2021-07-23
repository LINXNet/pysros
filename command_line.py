#!/Users/riccardo/virtualenvs/pysros/bin/python
import argparse
import logging
import textwrap
import time

import yaml

import napalm

logging.basicConfig()
#logging.getLogger('').setLevel(logging.DEBUG)


def time_func(func):
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
    help=textwrap.dedent("""
      Set logging verbose level. It accepts a number >= 0.
      The default value is 0, the minimal log besides stack backtrace is given;
      Verbose level 1 enables debug level logging for pyocnos;
      Verbose level 2 emits ncclient debug level logging as well.
      
      """)
  )

  args = parser.parse_args()
  if any(action in args.action for action in
         ['diff', 'replace', 'merge']) and not args.candidate_file_path:
    parser.error(
      "diff, replace and merge action requires -c, --candidate-file-path.")
  return args


@time_func
def main():
    args = parse_and_get_args()
    config_path = args.config_file_path
    switch_name = args.hostname
    operation = args.action
    running_conf_path = args.save_config_file_path
    candidate_conf_path = args.candidate_file_path
    format = args.format

    with open(config_path) as f:
        config = yaml.safe_load(f)['config']

    driver = napalm.get_network_driver('sros')
    with driver(hostname=switch_name,
                username=config['username'],
                timeout=180,
                password=config['password']) as device:
        if operation == 'running':
            result = device.get_config(retrieve='running',
                                      optional_args={"format": format}
                                      )
            with open(running_conf_path, 'w') as f:
                f.write(result['running'])

        elif operation == 'merge':
            device.load_merge_candidate(filename=candidate_conf_path)
            device.commit_config()

        elif operation == 'replace':
            device.load_replace_candidate(filename=candidate_conf_path)
            device.commit_config()

        elif operation == 'diff':
            device.load_replace_candidate(filename=candidate_conf_path)
            print(device.compare_config(optional_args={"json_format": True}))


if __name__ == '__main__':
    main()
