from strato.racktest.hostundertest import plugins
from strato.racktest.infra import suite
from strato.racktest.infra import rootfslabel


class InauguratorPlugin:
    _INAUGURATOR_KERNEL = "/usr/share/inaugurator/inaugurator.vmlinuz"
    _INAUGURATOR_INITRD = "/usr/share/inaugurator/inaugurator.initrd.img"

    def __init__(self, host):
        self._host = host

    def reinaugurate(
            self, rawLabel=None, rootfs=None, osmosisServerIPOverride=None, append=None):
        assert rawLabel is None or rootfs is None
        assert rawLabel is not None or rootfs is not None
        if rawLabel is None:
            rawLabel = rootfslabel.RootfsLabel(rootfs).label()
        commandLine = self._commandLine(rawLabel, osmosisServerIPOverride, append)
        self._host.ssh.ftp.putFile("/tmp/vmlinuz", self._INAUGURATOR_KERNEL)
        self._host.ssh.ftp.putFile("/tmp/initrd", self._INAUGURATOR_INITRD)
        self._host.ssh.run.script(
            "kexec --load /tmp/vmlinuz --initrd=/tmp/initrd --append='%s'" % commandLine)
        WAIT = 2
        self._host.ssh.run.backgroundScript("sleep %d; kexec -e" % WAIT)
        self._host.ssh.close()
        suite.sleep(WAIT + 0.5, "Sleeping for kexec to take place")

    def _commandLine(self, label, osmosisServerIP, append):
        if osmosisServerIP is None:
            osmosisServerIP = self._host.node.networkInfo()['osmosisServerIP']
        result = _INAUGURATOR_COMMAND_LINE % dict(
            macAddress=self._host.node.primaryMACAddress(),
            ipAddress=self._host.node.ipAddress(),
            netmask=self._host.node.networkInfo()['netmask'],
            gateway=self._host.node.networkInfo()['gateway'],
            osmosisServerIP=osmosisServerIP,
            label=label,
            rootPassword=self._host.node.rootSSHCredentials()['password'])
        if append is not None:
            result += ' --inauguratorPassthrough="%s"' % append
        return result


_INAUGURATOR_COMMAND_LINE = \
    "console=ttyS0,115200n8 " \
    "--inauguratorWithLocalObjectStore " \
    "--inauguratorSource=network " \
    "--inauguratorUseNICWithMAC=%(macAddress)s " \
    "--inauguratorOsmosisObjectStores=%(osmosisServerIP)s:1010 " \
    "--inauguratorNetworkLabel=%(label)s " \
    "--inauguratorIPAddress=%(ipAddress)s " \
    "--inauguratorNetmask=%(netmask)s " \
    "--inauguratorGateway=%(gateway)s " \
    "--inauguratorChangeRootPassword=%(rootPassword)s"


plugins.register('inaugurator', InauguratorPlugin)
