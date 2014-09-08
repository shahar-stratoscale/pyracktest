import unittest
import subprocess
import shutil
import json


class Test(unittest.TestCase):
    def setUp(self):
        shutil.rmtree('logs.racktest', ignore_errors=True)

    def test_firstExample(self):
        subprocess.check_call(
            './runner --scenariosRoot=example_racktests',
            shell=True, close_fds=True, stderr=subprocess.STDOUT)
        with open('logs.racktest/racktestrunnerreport.json') as f:
            report = json.load(f)
        self.assertEquals(len(report), 4)
        self.assertEquals(report[0]['scenario'], 'example_racktests/1_ping.py')
        self.assertTrue(report[0]['passed'])
        self.assertTrue(report[1]['passed'])
        self.assertTrue(report[2]['passed'])
        self.assertTrue(report[4]['passed'])


if __name__ == '__main__':
    unittest.main()
