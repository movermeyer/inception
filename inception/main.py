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

import os
import argparse
import logging
import subprocess
import zipfile

import jinja2
import inquirer

from version import APP

LOGGER = logging.getLogger(__name__)


class Variables(dict):
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super(Variables, cls).__new__(cls, **kwargs)
        return cls._instance

    def reset(self):
        self.clear()


class CallRun(object):
    def __init__(self, command):
        self._command = command

    def __call__(self, loader, output):
        LOGGER.debug('running CallRun("%s")', self._command)
        return subprocess.check_call(self._command, shell=True, cwd=output)


class CallCopy(object):
    def __init__(self, source='files'):
        self._source = source

    def __call__(self, loader, output):
        for path_content in loader.walk(self._source):
            path = os.path.join(output,
                                self._parse(path_content.relative_path))
            if path_content.is_dir:
                if not os.path.exists(path):
                    LOGGER.info('Creating directory %s', path)
                    os.makedirs(path)
                continue
            if path_content.is_file:
                if path_content.relative_path.endswith('.jinja'):
                    relative = path_content.relative_path[:-len('.jinja')]
                    content = self._parse(path_content.content)
                else:
                    relative = path_content.relative_path
                    content = path_content.content
                target = os.path.join(output, self._parse(relative))
                if os.path.exists(target):
                    LOGGER.warning(
                        'File "%s" already exists and will not be overriden.',
                        target)
                    continue
                self._write_result(target, content, path_content.permission)

    def _parse(self, template):
        return jinja2.Template(template).render(Variables())

    def _write_result(self, target, content, perms):
        LOGGER.debug('writting file %s', target)
        with open(target, 'w+') as fd:
            fd.write(content)
        os.chmod(target,  perms)


class CallPrompt(object):
    def __init__(self, questions=None):
        self._questions = questions

    def __call__(self, loader, output):
        questions = self._questions or loader.settings.get('QUESTIONS')
        if questions is None:
            LOGGER.debug('No questions to prompt')
            return

        if isinstance(questions, str):
            q = inquirer.load_from_json(questions)
        if isinstance(questions, list):
            q = inquirer.questions.load_from_list(questions)
        Variables().update(inquirer.prompt(q))


COMMANDS = dict(
    run=CallRun,
    copy=CallCopy,
    prompt=CallPrompt,
)


class PathContent(object):
    CAT_DIR = object()
    CAT_FILE = object()

    def __init__(self, category, relative_path, permission, content=None):
        self._category = category
        self.relative_path = relative_path
        self.permission = permission
        self.content = content

    @property
    def is_dir(self):
        return self._category == self.CAT_DIR

    @property
    def is_file(self):
        return self._category == self.CAT_FILE


class PathLoader(object):
    def __init__(self, path):
        self.path = path
        self._settings = None

    @property
    def settings(self):
        if self._settings is None:
            filename = os.path.join(self.path, 'settings.py')
            config = {}
            with open(filename) as fd:
                exec(fd.read(), COMMANDS.copy(), config)
            self._settings = config
        return self._settings

    def walk(self, relative_path):
        source = os.path.join(self.path, relative_path)
        LOGGER.debug('walking over ("%s")', source)
        basepathlen = len(source) + 1

        for root, dirs, files in os.walk(source):
            for d in dirs:
                origin = os.path.join(root, d)
                path = origin[basepathlen:]
                perms = os.stat(origin).st_mode
                yield PathContent(PathContent.CAT_DIR, path, perms)
            for f in files:
                origin = os.path.join(root, f)
                path = origin[basepathlen:]
                perms = os.stat(origin).st_mode
                with open(origin) as fd:
                    yield PathContent(PathContent.CAT_FILE, path, perms,
                                      fd.read())


class ZipLoader(object):
    def __init__(self, ):
        pass


def get_loader(path):
    if os.path.isdir(path):
        return PathLoader(path)
    if zipfile.is_zipfile(path):
        return ZipLoader(path)
    # FIXME: raise exception


class Runner(object):
    def __init__(self, loader):
        self._loader = loader

    def run(self, output):
        program = (self._loader.settings.get('PROGRAM')
                   or [CallPrompt(), CallCopy()])

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
    LOGGER.addHandler(handler)
    LOGGER.setLevel(LEVEL)
    LOGGER.debug('Verbose mode activated')


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
