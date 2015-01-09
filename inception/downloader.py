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
import urllib2
import shelve
import shutil

import loader

LOGGER = logging.getLogger('inception.' + __name__)
DATA_PATH = os.path.join(os.environ['HOME'], '.inception')


class DownloaderException(object):
    pass


class PackageNotFoundError(DownloaderException):
    pass


class VersionNotFoundError(DownloaderException):
    pass


class Downloader(object):
    CACHE = os.path.join(DATA_PATH, 'cache')
    INDEX_URL = ''

    def fetch_file(self, url):
        response = urllib2.urlopen(url)
        return response.read()

    def fetch_index(self):
        return self.fetch_file(self.INDEX_URL)


class Database(object):
    DATA_FILE = os.path.join(DATA_PATH, 'data.shelve')

    def get(self, name):
        try:
            data = self._open()
            return data[name]
        finally:
            data.close()

    def insert(self, name, url):
        try:
            data = self._open()
            data[name] = url
        finally:
            data.close()

    def _open(self):
        if not os.path.exists(DATA_PATH):
            os.path.makedirs(DATA_PATH)

        return shelve.open(self.DATA_FILE)


class FileManager(object):
    REPO_PATH = os.path.join(DATA_PATH, 'repository')

    def get_list_of_versions(self, name):
        path = os.path.join(self.REPO_PATH, name)
        if not os.path.exits(path):
            return []
        return [x.split('.') for x in os.listdir(path)]

    def load(self, name, version=None):
        version = version or max(self.get_list_of_versions(name))
        path = os.path.join(self.REPO_PATH, name, version)
        zipfile = os.path.join(path, 'package.zip')

        if not os.path.exists(path):
            raise VersionNotFoundError()
        if not os.path.exists(zipfile):
            raise PackageNotFoundError()
        return loader.get_loader(zipfile)

    def save(self, source):
        zloader = loader.get_loader(source)
        zloader.validate()
        path = os.path.join(self.REPO_PATH, zloader.name, zloader.version_str)
        zipfile = os.path.join(path, 'package.zip')

        if not os.path.exists(path):
            os.makedirs(path)
        LOGGER.debug('Storing in %s', path)
        if os.path.isfile(source):
            shutil.copy2(source, path)
        elif os.path.isdir(source):
            shutil.copytree(source, path)
