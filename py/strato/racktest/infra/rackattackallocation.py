from rackattack import clientfactory
from rackattack import api
from strato.racktest.infra import config
import logging
import multiprocessing.pool
from strato.racktest.infra import suite
from strato.racktest.infra import rootfslabel
from strato.racktest import hostundertest


class RackAttackAllocation:
    _TIMEOUT = 10 * 60

    def __init__(self, hosts):
        self._hosts = hosts
        self._client = clientfactory.factory()
        self._allocation = self._client.allocate(
            requirements=self._rackattackRequirements(), allocationInfo=self._rackattackAllocationInfo())
#       self._allocation.setForceReleaseCallback()
        try:
            self._allocation.wait(timeout=self._TIMEOUT)
        except:
            logging.exception("Allocation failed, attempting post mortem")
            self._postMortemAllocation()
            raise
        self._nodes = self._allocation.nodes()
        assert suite.runOnEveryHost is None
        suite.runOnEveryHost = self.runOnEveryHost

    def nodes(self):
        return self._nodes

    def free(self):
        assert suite.runOnEveryHost == self.runOnEveryHost
        suite.runOnEveryHost = None
        self._allocation.free()

    def _rackattackRequirements(self):
        result = {}
        for name, requirements in self._hosts.iteritems():
            rootfs = rootfslabel.RootfsLabel(requirements['rootfs'])
            hardwareConstraints = dict(requirements)
            del hardwareConstraints['rootfs']
            result[name] = api.Requirement(
                imageLabel=rootfs.label(), imageHint=rootfs.imageHint(),
                hardwareConstraints=hardwareConstraints)
        return result

    def _rackattackAllocationInfo(self):
        return api.AllocationInfo(user=config.USER, purpose="racktest")

    def runOnEveryHost(self, callback, description):
        pool = multiprocessing.pool.ThreadPool(processes=len(self._nodes))
        try:
            futures = [
                pool.apply_async(self._safeRun, args=(callback, description, name))
                for name in self._nodes]
            for future in futures:
                future.wait(timeout=2 ** 31)
            for future in futures:
                future.get()
        finally:
            pool.close()

    def _safeRun(self, callback, description, name):
        try:
            callback(name)
        except:
            logging.exception("When %(description)s on '%(name)s'", dict(
                description=description, name=name))
            raise

    def _postMortemAllocation(self):
        try:
            nodes = self._allocation.nodes()
        except:
            logging.exception("Unable to get nodes of a failed allocation, post mortem aborts")
            return
        for name, node in nodes.iteritems():
            host = hostundertest.host.Host(node, name)
            try:
                host.logbeam.postMortemSerial()
            except:
                logging.error("Unable to collect serial logs of host %(id)s", dict(id=host.id()))
