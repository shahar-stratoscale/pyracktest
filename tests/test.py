import unittest
import subprocess
import shutil
import json
import os
import tempfile


class Test(unittest.TestCase):
    def setUp(self):
        shutil.rmtree('logs.racktest', ignore_errors=True)

    def test_examples(self):
        params = os.environ.get('RACKTEST_ADDITIONAL_PARAMS', '')
        subprocess.check_call(
            './runner --scenariosRoot=example_racktests ' + params,
            shell=True, close_fds=True, stderr=subprocess.STDOUT)
        with open('logs.racktest/racktestrunnerreport.json') as f:
            report = json.load(f)
        self.assertEquals(len(report), 8)
        scenarios = [o['scenario'] for o in report]
        self.assertIn('example_racktests/1_ping.py', scenarios)
        self.assertTrue(report[0]['passed'])
        self.assertTrue(report[1]['passed'])
        self.assertTrue(report[2]['passed'])
        self.assertTrue(report[3]['passed'])
        self.assertTrue(report[4]['passed'])
        self.assertTrue(report[5]['passed'])
        self.assertTrue(report[6]['passed'])
        self.assertTrue(report[7]['passed'])

    def test_failingTests(self):
        failedCorrectlyLog = tempfile.NamedTemporaryFile()
        os.environ['FAILED_CORRECTLY_LOG'] = failedCorrectlyLog.name
        params = os.environ.get('RACKTEST_ADDITIONAL_PARAMS', '')
        result = subprocess.call(
            './runner --scenariosRoot=example_failing_racktests ' + params,
            shell=True, close_fds=True, stderr=subprocess.STDOUT)
        self.assertNotEqual(result, 0)
        with open('logs.racktest/racktestrunnerreport.json') as f:
            report = json.load(f)
        self.assertEquals(len(report), 1)
        scenarios = [o['scenario'] for o in report]
        self.assertIn('example_failing_racktests/1_timeout.py', scenarios)
        self.assertFalse(report[0]['passed'])
        correctlyFailed = failedCorrectlyLog.read().strip().split("\n")
        self.assertNotEqual(correctlyFailed, [""])


if __name__ == '__main__':
    unittest.main()
