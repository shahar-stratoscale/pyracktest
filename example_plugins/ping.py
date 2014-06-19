from strato.racktest.hostundertest import plugins


class Ping:
    def __init__(self, host):
        self._host = host

    def once(self, host):
        self._host.ssh.run.script("ping -c 1 %s" % host.node.ipAddress())


plugins.register('ping', Ping)
