#!/usr/bin/env python

# Copyright (C) 2014 Miguel Angel Garcia <miguelangel.garcia@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import logging

from version import APP
from loader import get_loader
from commands import DEFAULT_PROGRAM

LOGGER = logging.getLogger('inception.' + __name__)


class Runner(object):
    def __init__(self, loader):
        self._loader = loader

    def run(self, output):
        program = (self._loader.settings.get('PROGRAM')
                   or DEFAULT_PROGRAM)

        for command in program:
            LOGGER.debug('New program command: %s', command)
            if callable(command):
                command(self._loader, output)
                continue
            else:
                LOGGER.error('Unsupported command: %s', command)


def logging_setup(verbose):
    if verbose:
        FORMAT = '%(asctime)s [%(levelname)s] %(message)s'
        DATEFORMAT = ''
        LEVEL = logging.DEBUG
    else:
        FORMAT = '%()s %(message)s'
        DATEFORMAT = ''
        LEVEL = logging.INFO
    formatter = logging.Formatter(FORMAT, DATEFORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger = logging.getLogger('inception')
    logger.addHandler(handler)
    logger.setLevel(LEVEL)
    logger.debug('Verbose mode activated')


def main():
    parser = argparse.ArgumentParser(description=APP.description)
    parser.add_argument('--template-path', dest="path", required=True,
                        help='Path to template to be applied.')

    parser.add_argument('-o', '--output',
                        help='Where the output should be put.')

    parser.add_argument('--verbose', action="store_true", default=False,
                        help='Verbose mode.')

    args = parser.parse_args()

    logging_setup(args.verbose)

    loader = get_loader(args.path)
    runner = Runner(loader)
    runner.run(args.output)


if __name__ == '__main__':
    main()
