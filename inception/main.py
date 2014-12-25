#!/usr/bin/env python

import os
import argparse
import jinja2

import inquirer

from version import APP


class Loader(object):
    def __init__(self, path):
        self._path = path

    @property
    def config(self):
        filename = os.path.join(self._path, 'settings.py')
        config = {}
        a = {}
        with open(filename) as fd:
            exec(fd.read(), {}, config)
        return config


class Runner(object):
    def __init__(self, loader):
        self._loader = loader
        self._config = None
        self._variables = None

    def run(self):
        self.load_config()
        self.inquire()
        self.apply()

    def load_config(self):
        self._config = self._loader.config

    def inquire(self):
        questions = self._config.get('QUESTIONS')
        if questions is None:
            return
        if isinstance(questions, str):
            q = inquirer.load_from_json(questions)
            self._variables = inquirer.prompt(q)
        if isinstance(questions, list):
            q = inquirer.questions.load_from_list(questions)
            self._variables = inquirer.prompt(q)

    def apply(self):
        pass
        # To be done: walk over self._config._path and:
        #   - create every directory mirror
        #   - apply the template and save it in the mirror.

        #template = jinja2.Template('Hello {{ name }}!')
        #template.render(name='John Doe')


def main():
    parser = argparse.ArgumentParser(description=APP.description)
    parser.add_argument('--path', required=True,
                        help='Path to template to be applied.')

    args = parser.parse_args()

    loader = Loader(args.path)
    runner = Runner(loader)
    runner.run()


if __name__ == '__main__':
    main()
