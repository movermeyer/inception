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
        self._metadata = None

    @property
    def settings(self):
        if self._settings is None:
            self.load_settings()
        return self._settings

    @property
    def metadata(self):
        if self._metadata is None:
            self.load_metadata()
        return self._metadata

    def load_settings(self):
        self._settings = self.load_python('settings.py')

    def load_metadata(self):
        self._metadata = self.load_python('metadata.py')

    def walk(self, relative_path):
        raise NotImplemented('Abstract method')


class PathLoader(Loader):
    def load_python(self, filename):
        filename = os.path.join(self.path, filename)
        config = {}
        with open(filename) as fd:
            exec(fd.read(), COMMANDS.copy(), config)
        return config

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
    def load_python(self, filename):
        with zipfile.ZipFile(self.path) as z:
            with z.open(filename) as fd:
                config = {}
                exec(fd.read(), COMMANDS.copy(), config)
        return config

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
