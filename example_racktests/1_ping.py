from strato.racktest.infra.suite import *
import example_plugins.ping


class Test:
    HOSTS = dict(first=dict(rootfs="rootfs-vanilla"), second=dict(rootfs="rootfs-basic"))

    def run(self):
        host.first.ssh.run.script("ping -c 1 %s" % host.second.node.ipAddress())
        host.second.ping.once(host.first)
