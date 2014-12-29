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
import logging
import zipfile

from commands import COMMANDS

LOGGER = logging.getLogger('inception.' + __name__)


class PathContent(object):
    CAT_DIR = object()
    CAT_FILE = object()

    def __init__(self, category, relative_path, permission=None, content=None):
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


class Loader(object):
    def __init__(self, path):
        self.path = path
        self._settings = None

    @property
    def settings(self):
        if self._settings is None:
            self.load_settings()
        return self._settings

    def walk(self, relative_path):
        raise NotImplemented('Abstract method')


class PathLoader(Loader):
    def load_settings(self):
        filename = os.path.join(self.path, 'settings.py')
        config = {}
        with open(filename) as fd:
            exec(fd.read(), COMMANDS.copy(), config)
        self._settings = config

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


class ZipLoader(Loader):
    def load_settings(self):
        with zipfile.ZipFile(self.path) as z:
            with z.open('settings.py') as fd:
                config = {}
                exec(fd.read(), COMMANDS.copy(), config)
        self._settings = config

    def walk(self, relative_path):
        dirs = set()
        with zipfile.ZipFile(self.path) as z:
            for name in z.namelist():
                path = os.path.dirname(name)
                if path not in dirs:
                    yield PathContent(PathContent.CAT_DIR, path)
                    dirs.add(path)
                yield PathContent(PathContent.CAT_FILE, name,
                                  None, z.read(name))


def get_loader(path):
    if os.path.isdir(path):
        return PathLoader(path)
    if zipfile.is_zipfile(path):
        return ZipLoader(path)
    # FIXME: raise exception
