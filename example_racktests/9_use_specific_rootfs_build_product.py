from strato.racktest.infra.suite import *


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic__rootfs"))

    def run(self):
        TS_ASSERT("hello" in host.it.ssh.run.script("echo hello"))
