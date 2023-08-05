#!/usr/bin/python
# coding: utf-8
# Author: Mario Lenz <m@riolenz.de>
# License: GPLv3+
# Copyright: Ansible Project, 2022
"""The ansible-community CLI program."""

import argparse


def main():
    '''Main entrypoint for the ansible-community CLI program.'''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--version',
        action='version',
        version='Ansible community version 6.0.0',
        help="show the version of the Ansible community package",
    )
    parser.parse_args()
    parser.print_help()


if __name__ == '__main__':
    main()
