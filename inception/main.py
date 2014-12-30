#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (C) 2014 Miguel Angel Garcia <miguelangel.garcia@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
