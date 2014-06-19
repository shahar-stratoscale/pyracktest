from rackattack import clientfactory
from rackattack import api
import subprocess
from strato.racktest.infra import config
import logging
import multiprocessing.pool


class RackAttackAllocation:
    _TIMEOUT = 5 * 60

    def __init__(self, hosts):
        self._hosts = hosts
        self._client = clientfactory.factory()
        self._allocation = self._client.allocate(
            requirements=self._rackattackRequirements(), allocationInfo=self._rackattackAllocationInfo())
#       self._allocation.setForceReleaseCallback()
        self._allocation.wait(timeout=self._TIMEOUT)
        self._nodes = self._allocation.nodes()

    def nodes(self):
        return self._nodes

    def free(self):
        self._allocation.free()

    def _rackattackRequirements(self):
        result = {}
        for name, requirements in self._hosts.iteritems():
            rootfs = requirements['rootfs']
            label = subprocess.check_output([
                "solvent", "printlabel", "--repositoryBasename", rootfs, "--product=rootfs"]).strip()
            hardwareConstraints = dict(requirements)
            del hardwareConstraints['rootfs']
            result[name] = api.Requirement(
                imageLabel=label, imageHint=rootfs, hardwareConstraints=hardwareConstraints)
        return result

    def _rackattackAllocationInfo(self):
        return api.AllocationInfo(user=config.USER, purpose="racktest")

    def runOnEvery(self, callback, description):
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
