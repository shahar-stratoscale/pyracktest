import logging
from strato.racktest.infra import suite
from strato.racktest.infra import rackattackallocation
from strato.racktest import hostundertest
import strato.racktest.hostundertest.host
from strato.whiteboxtest.infra import timeoutthread
from strato.common.log import discardinglogger
import os
import signal
import time
import sys


class Executioner:
    ABORT_TEST_TIMEOUT_DEFAULT = 10 * 60
    DISCARD_LOGGING_OF = (
        'paramiko',
        'selenium.webdriver.remote.remote_connection',
        'requests.packages.urllib3.connectionpool')

    def __init__(self, klass):
        self._test = klass()
        self._testTimeout = getattr(self._test, 'ABORT_TEST_TIMEOUT', self.ABORT_TEST_TIMEOUT_DEFAULT)

    def host(self, name):
        return self._hosts[name]

    def hosts(self):
        return self._hosts

    def executeTestScenario(self):
        timeoutthread.TimeoutThread(self._testTimeout, self._testTimedOut)
        logging.info("Test timer armed. Timeout in %(seconds)d seconds", dict(seconds=self._testTimeout))
        discardinglogger.discardLogsOf(self.DISCARD_LOGGING_OF)
        self._hosts = dict()
        suite.findHost = self.host
        suite.hosts = self.hosts
        if not hasattr(self._test, 'host'):
            self._test.host = self.host
        if not hasattr(self._test, 'hosts'):
            self._test.hosts = self.hosts
        logging.info("Allocating Nodes")
        self._allocation = rackattackallocation.RackAttackAllocation(self._test.HOSTS)
        logging.progress("Done allocating nodes")
        try:
            self._setUp()
            try:
                self._run()
            finally:
                self._tearDown()
        finally:
            try:
                self._allocation.free()
            except:
                logging.exception("Unable to free allocation")

    def _testTimedOut(self):
        logging.error(
            "Timeout: test is running for more than %(seconds)ds, aborting. You might need to increase "
            "the scenario ABORT_TEST_TIMEOUT", dict(seconds=self._testTimeout))
        timeoutthread.TimeoutThread(10, self._killSelf)
        timeoutthread.TimeoutThread(15, self._killSelfHard)
        self._killSelf()
        time.sleep(2)
        self._killSelfHard()

    def _killSelf(self):
        os.kill(os.getpid(), signal.SIGTERM)

    def _killSelfHard(self):
        os.kill(os.getpid(), signal.SIGKILL)

    def _filename(self):
        filename = sys.modules[self._test.__class__.__module__].__file__
        if filename.endswith(".pyc"):
            filename = filename[: -1]
        return filename

    def _setUpHost(self, name):
        host = hostundertest.host.Host(self._allocation.nodes()[name], name)
        logging.info("Host allocated: %(name)s: %(credentials)s", dict(
            name=name, credentials=host.node.rootSSHCredentials()))
        try:
            host.ssh.waitForTCPServer()
            host.ssh.connect()
        except:
            logging.error(
                "Rootfs did not wake up after inauguration. Saving serial file in postmortem dir "
                "host %(id)s name %(name)s", dict(id=host.node.id(), name=name))
            host.logbeam.postMortemSerial()
            raise
        self._hosts[name] = host
        getattr(self._test, 'setUpHost', lambda x: x)(name)

    def _setUp(self):
        logging.info("Setting up test in '%(filename)s'", dict(filename=self._filename()))
        self._allocation.runOnEveryHost(self._setUpHost, "Setting up host")
        try:
            getattr(self._test, 'setUp', lambda: None)()
        except:
            logging.exception(
                "Failed setting up test in '%(filename)s'", dict(filename=self._filename()))
            suite.outputExceptionStackTrace()
            raise

    def _run(self):
        logging.progress("Running test in '%(filename)s'", dict(filename=self._filename()))
        try:
            self._test.run()
            logging.success(
                "Test completed successfully, in '%(filename)s', with %(asserts)d successfull asserts",
                dict(filename=self._filename(), asserts=suite.successfulTSAssertCount()))
            print ".:1: Test passed"
        except:
            logging.exception("Test failed, in '%(filename)s'", dict(filename=self._filename()))
            suite.outputExceptionStackTrace()
            raise

    def _tearDown(self):
        logging.info("Tearing down test in '%(filename)s'", dict(filename=self._filename()))
        try:
            getattr(self._test, 'tearDown', lambda: None)()
        except:
            logging.exception(
                "Failed tearing down test in '%(filename)s'", dict(filename=self._filename()))
            suite.outputExceptionStackTrace()
            raise
        tearDownHost = getattr(self._test, 'tearDownHost', lambda x: x)
        self._allocation.runOnEveryHost(tearDownHost, "Tearing down host")
