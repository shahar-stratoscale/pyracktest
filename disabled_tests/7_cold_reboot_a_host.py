from strato.racktest.infra.suite import *


class Test:
    HOSTS = dict(it=dict(rootfs="rootfs-basic"))

    def run(self):
        try:
            host.it.ssh.ftp.putContents("/mark", "mark")
            host.it.ssh.run.script("sync")
            host.it.ssh.close()
            host.it.node.coldRestart()
            logging.progress("Waiting for ssh to respond")
            host.it.ssh.waitForTCPServer(timeout=7 * 60)
            logging.progress("Waiting for ssh to connect")
            host.it.ssh.connect()
            TS_ASSERT('hello' in host.it.ssh.run.script("echo hello"))
            TS_ASSERT('mark' in host.it.ssh.ftp.getContents("/mark"))
        finally:
            host.it.logbeam.postMortemSerial()
