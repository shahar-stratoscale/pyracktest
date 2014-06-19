from rackattack.ssh import connection
from strato.racktest.hostundertest import plugins

import strato.racktest.hostundertest.builtinplugins.rpm


class Host:
    def __init__(self, rackattackNode):
        self.node = rackattackNode
        self.ssh = connection.Connection(** rackattackNode.rootSSHCredentials())
        self.__plugins = {}

    def __getattr__(self, name):
        if name not in self.__plugins:
            self.__plugins[name] = plugins.plugins[name](self)
        return self.__plugins[name]
