from strato.racktest.infra.suite import *
from strato.racktest.hostundertest.optionalplugins import inauguratorplugin


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic"))

    def run(self):
        kernelCommandLine = host.it.ssh.run.script("cat /proc/cmdline")
        TS_ASSERT('unparsed' not in kernelCommandLine)
        host.it.inaugurator.reinaugurate(rootfs="rootfs-basic", append="unparsed")
        host.it.ssh.waitForTCPServer(timeout=7 * 60)
        host.it.ssh.connect()
        kernelCommandLine = host.it.ssh.run.script("cat /proc/cmdline")
        TS_ASSERT('unparsed' in kernelCommandLine)
