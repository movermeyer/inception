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

import os
import subprocess
import logging
import jinja2
import inquirer

from variables import Variables


LOGGER = logging.getLogger('inception.' + __name__)


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
        if perms is not None:
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

DEFAULT_PROGRAM = (CallPrompt(), CallCopy())
