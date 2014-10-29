import unittest
import subprocess
import shutil
import json
import os


class Test(unittest.TestCase):
    def setUp(self):
        shutil.rmtree('logs.racktest', ignore_errors=True)

    def test_firstExample(self):
        params = os.environ.get('RACKTEST_ADDITIONAL_PARAMS', '')
        subprocess.check_call(
            './runner --scenariosRoot=example_racktests ' + params,
            shell=True, close_fds=True, stderr=subprocess.STDOUT)
        with open('logs.racktest/racktestrunnerreport.json') as f:
            report = json.load(f)
        self.assertEquals(len(report), 6)
        scenarios = [o['scenario'] for o in report]
        self.assertIn('example_racktests/1_ping.py', scenarios)
        self.assertTrue(report[0]['passed'])
        self.assertTrue(report[1]['passed'])
        self.assertTrue(report[2]['passed'])
        self.assertTrue(report[3]['passed'])
        self.assertTrue(report[4]['passed'])
        self.assertTrue(report[5]['passed'])


if __name__ == '__main__':
    unittest.main()
