
import os
import shutil
import unittest
import pexpect

class TestBasic(unittest.TestCase):
    def setUp(self):
        if os.path.exists('output'):
            shutil.rmtree('output')

    def tearDown(self):
        if os.path.exists('output'):
            shutil.rmtree('output')

    def test_foo(self):
        p = pexpect.spawn('python inception/__main__.py --template-path example -o output --verbose')
        p.expect('name:', timeout=1)
        p.sendline('foo')
        p.expect('surname:', timeout=1)
        p.sendline('bar')
        p.expect('Micro', timeout=1)
        p.sendline('')
        p.wait()
