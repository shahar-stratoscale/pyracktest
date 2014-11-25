from strato.racktest.infra.suite import *
import subprocess

ROOTFS_LABEL = subprocess.check_output([
    "solvent", "printlabel", "--product=rootfs", "--repositoryBasename=rootfs-basic"]).strip()


class Test:
    HOSTS = dict(it=dict(rootfs=ROOTFS_LABEL))

    def run(self):
        TS_ASSERT("hello" in host.it.ssh.run.script("echo hello"))
