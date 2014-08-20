from strato.whiteboxtest.infra.suite import *

findHost = None
hosts = None
runOnEveryHost = None


class _HostsGetter:
    def __getattr__(self, name):
        return findHost(name)

    def __call__(self, name):
        return findHost(name)


host = _HostsGetter()
