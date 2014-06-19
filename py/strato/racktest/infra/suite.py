from strato.whiteboxtest.infra.suite import *

findHost = None


class _HostsGetter:
    def __getattr__(self, name):
        return findHost(name)


host = _HostsGetter()
