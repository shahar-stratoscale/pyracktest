#!/usr/bin/python

from strato.racktest.infra import config
from strato.common.log import configurelogging
configurelogging.configureLogging('racktest.runner', forceDirectory=config.TEST_LOGS_DIR)
import logging
import argparse
import sys
import glob
import time
import json
import re
import os
import subprocess
from strato.racktest.infra import suite
from strato.racktest import runner

_defaultReport = os.path.join(config.TEST_LOGS_DIR, "racktestrunnerreport.json")
_defaultLiveReport = os.path.join(config.TEST_LOGS_DIR, "racktestrunnerlivereport.json")
_single = os.path.join(os.path.dirname(runner.__file__), "single.py")

parser = argparse.ArgumentParser(
    description="run Integration test scenarios. If no arguments given, run all rack scenarios")
parser.add_argument(
    "--interactOnAssert", help="go into interact mode on assert", action='store_true')
parser.add_argument("--regex", default="", help="run all scenarios matching the regular expression")
parser.add_argument('--listOnly', action='store_true', help='list scenarios and exit')
parser.add_argument('--liveReportFilename', default=_defaultLiveReport)
parser.add_argument("--reportFilename", default=_defaultReport)
parser.add_argument("--scenariosRoot", default="racktests")
parser.add_argument("--configurationFile", default="/etc/racktest.conf")
args = parser.parse_args()
if args.interactOnAssert:
    suite.enableInteractOnAssert()
config.load(args.configurationFile)


class Runner:
    def __init__(self, args):
        self._args = args
        self._scenarios = self._matchingScenarios()
        if len(self._scenarios) == 0:
            raise Exception("No scenarios files found")
        self._currentlyRunning = {}
        self._results = []

    def run(self):
        for scenario in self._scenarios:
            self._currentlyRunning['localhost'] = dict(filename=scenario)
            self._dumpLiveReport()
            self._runScenario(scenario)

    def total(self):
        return len(self._scenarios)

    def passedCount(self):
        return len([res for res in self._results if res['passed']])

    def failedCount(self):
        return self.total() - self.passedCount()

    def failed(self):
        return [res['scenario'] for res in self._results if not res['passed']]

    def writeReport(self):
        with open(self._args.reportFilename, "w") as f:
            json.dump(self._results, f)

    def _matchingScenarios(self):
        root = self._args.scenariosRoot
        scenarios = \
            glob.glob(root + "/*.py") + \
            glob.glob(root + "/*/*.py") + \
            glob.glob(root + "/*/*/*.py") + \
            glob.glob(root + "/*/*/*/*.py")
        for scenario in scenarios:
            if scenario.endswith("/__init__.py"):
                raise Exception("'__init__.py' must not be found under the scenarios directory")
        scenarios.sort()
        return [s for s in scenarios if re.search(self._args.regex, s) is not None]

    def _dumpLiveReport(self):
        everything = dict(
            results=self._results, currentlyRunning=self._currentlyRunning, scenarios=self._scenarios)
        with open(self._args.liveReportFilename, "w") as f:
            json.dump(everything, f)

    def _runScenario(self, scenario):
        before = time.time()
        result = subprocess.call(['python', _single, args.configurationFile, scenario], close_fds=True)
        took = time.time() - before
        self._results.append(dict(scenario=scenario, passed=result == 0, timeTook=took, host='localhost'))


runner = Runner(args)
runner.run()
runner.writeReport()
if runner.passedCount() < runner.total():
    logging.error(
        "%(failed)d tests Failed. %(passed)d/%(total)d Passed",
        dict(failed=runner.failedCount(), passed=runner.passedCount(), total=runner.total()))
    for scenario in runner.failed():
        logging.error("Failed scenario: %(scenario)s", dict(scenario=scenario))
    sys.exit(1)
else:
    logging.success(
        "Tests Passed: %(passed)d/%(total)d", dict(passed=runner.passedCount(), total=runner.total()))
