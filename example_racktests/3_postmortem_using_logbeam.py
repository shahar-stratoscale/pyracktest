from strato.racktest.infra.suite import *
from strato.racktest.infra import logbeamfromlocalhost
import os
from strato.common import log
import time
import shutil
import tempfile
import logging


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic"))

    def run(self):
        shutil.rmtree(os.path.join(log.config.LOGS_DIRECTORY, "it"), ignore_errors=True)
        expectedFile = os.path.join(log.config.LOGS_DIRECTORY, "it", "postmortem", 'df')
        serialLogFile = os.path.join(log.config.LOGS_DIRECTORY, "it", "postmortem", "serial.txt")
        uniqueString = 'time: ' + str(time.time())
        host.it.ssh.run.script("echo %s > /dev/console" % uniqueString)
        TS_ASSERT(not os.path.exists(expectedFile))
        TS_ASSERT(not os.path.exists(serialLogFile))
        host.it.logbeam.postMortem()
        logging.progress("Expected file: %(expectedFile)s", dict(expectedFile=expectedFile))
        TS_ASSERT(os.path.exists(expectedFile))
        TS_ASSERT(os.path.exists(serialLogFile))
        contents = open(serialLogFile).read()
        TS_ASSERT(uniqueString in contents)
        self.useLogBeamFromLocal()
        self.beamADirectory()

    def useLogBeamFromLocal(self):
        tempDir = tempfile.mkdtemp()
        try:
            with open(os.path.join(tempDir, "someLog.txt"), "w") as f:
                f.write("hello")
            logbeamfromlocalhost.beam([os.path.join(tempDir, "someLog.txt")])
        finally:
            shutil.rmtree(tempDir, ignore_errors=True)
        expectedFile = os.path.join(log.config.LOGS_DIRECTORY, "someLog.txt")
        TS_ASSERT(os.path.exists(expectedFile))

    def beamADirectory(self):
        host.it.ssh.run.script("mkdir /tmp/aDirectory")
        host.it.ssh.run.script("echo hello > /tmp/aDirectory/bye")
        host.it.logbeam.beam("/tmp/aDirectory/")
        expectedFile = os.path.join(log.config.LOGS_DIRECTORY, "it", "bye")
        logging.progress("Expected file: %(expectedFile)s", dict(expectedFile=expectedFile))
        TS_ASSERT(os.path.exists(expectedFile))
