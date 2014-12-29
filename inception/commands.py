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
