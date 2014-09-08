from strato.racktest.infra.suite import *
import re


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic", minimumRAMGB=4))

    def run(self):
        memInfo = host.it.ssh.run.script("cat /proc/meminfo")
        total = int(re.search(r'MemTotal:\s*(\d+)\s+kB', memInfo).group(1))
        TS_ASSERT_LESS_THAN(4 * 1024 * 1024 * 0.9, total)
