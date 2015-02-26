from strato.racktest.infra.suite import *
import time
import os


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-complicated"))
    ABORT_TEST_TIMEOUT = 60

    def run(self):
        time.sleep(120)

    def onTimeout(self):
        open(os.environ['FAILED_CORRECTLY_LOG'], "a").write("1_timeout failed correctly\n")
