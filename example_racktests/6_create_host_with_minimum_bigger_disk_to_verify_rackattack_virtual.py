from strato.racktest.infra.suite import *


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic", minimumDisk1SizeGB=20))

    def run(self):
        partitions = host.it.ssh.run.script("cat /proc/partitions")
        vdaSizeKB = int(partitions.split('\n')[2][13:13 + 12].strip())
        TS_ASSERT_LESS_THAN(18, vdaSizeKB / 1024 / 1024)
