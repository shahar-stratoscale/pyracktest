from strato.racktest.infra.suite import *
from strato.racktest.hostundertest.optionalplugins import inauguratorplugin


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic"))

    def run(self):
        kernelCommandLine = host.it.ssh.run.script("cat /proc/cmdline")
        TS_ASSERT('unparsed' not in kernelCommandLine)

        host.it.inaugurator.reinaugurate(rootfs="rootfs-basic", append="unparsed")
        logging.progress("Waiting for ssh to respond")
        host.it.ssh.waitForTCPServer(timeout=7 * 60)
        host.it.ssh.connect()
        kernelCommandLine = host.it.ssh.run.script("cat /proc/cmdline")
        logging.info("kernel command line: %(commandLine)s", dict(commandLine=kernelCommandLine))
        if 'unparsed' in kernelCommandLine:
            TS_ASSERT('unparsed' in kernelCommandLine)
            logging.progress("Successfully reinaugurated")
        else:
            host.it.logbeam.postMortemSerial()
            serialLog = host.it.node.fetchSerialLog()
            TS_ASSERT('Kernel panic - not syncing: Fatal hardware error!' in serialLog)
            logging.warning(
                "under fatal hardware error, a second reboot takes place and fails the "
                "kernel command line passing. Hopefully this will be resolved "
                "at future kernel versions. For now it's an empty test-pass")
