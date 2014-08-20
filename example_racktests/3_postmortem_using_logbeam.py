from strato.racktest.infra.suite import *
import os
from strato.common import log
import shutil


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic"))

    def run(self):
        shutil.rmtree(os.path.join(log.config.LOGS_DIRECTORY, "it"), ignore_errors=True)
        expectedFile = os.path.join(log.config.LOGS_DIRECTORY, "it", "postmortem", 'df')
        TS_ASSERT(not os.path.exists(expectedFile))
        host.it.logbeam.postMortem()
        TS_ASSERT(os.path.exists(expectedFile))
