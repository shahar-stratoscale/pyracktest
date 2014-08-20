from rackattack.ssh import connection
from strato.racktest.hostundertest import plugins

import strato.racktest.hostundertest.builtinplugins.rpm
import strato.racktest.hostundertest.builtinplugins.seed
import strato.racktest.hostundertest.builtinplugins.logbeamplugin


class Host:
    def __init__(self, rackattackNode, name):
        self.node = rackattackNode
        self.name = name
        self.ssh = connection.Connection(** rackattackNode.rootSSHCredentials())
        self.__plugins = {}

    def __getattr__(self, name):
        if name not in self.__plugins:
            self.__plugins[name] = plugins.plugins[name](self)
        return self.__plugins[name]
