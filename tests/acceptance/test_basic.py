import os
import shutil
import unittest
import pexpect
import time


class TestBasic(unittest.TestCase):
    def setUp(self):
        if os.path.exists('output'):
            shutil.rmtree('output')

    def tearDown(self):
        if os.path.exists('output'):
            shutil.rmtree('output')

    def test_foo(self):
        p = pexpect.spawn(
            'python inception/__main__.py --template-path examples/basic '
            '-o output --verbose'
        )
        p.expect('name:', timeout=1)
        p.sendline('foo')
        p.expect('surname:', timeout=1)
        p.sendline('bar')
        p.expect('Micro', timeout=1)
        p.sendline('\x0d')
        while p.isalive():
            time.sleep(0.1)

        assert os.path.exists('output/example1.txt')
        assert os.path.exists('output/example2.txt')
        assert os.path.exists('output/foo/bar/bazz.txt')
        assert os.path.exists('output/foo/bar/foo.txt')
        with open('output/example2.txt') as fd:
            assert 'this is a template file foo' == fd.read()
