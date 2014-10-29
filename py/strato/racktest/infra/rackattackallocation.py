from rackattack import clientfactory
from rackattack import api
from strato.racktest.infra import config
import logging
from strato.racktest.infra import concurrently
from strato.racktest.infra import suite
from strato.racktest.infra import rootfslabel
import tempfile
import os
import shutil
import codecs
from strato.racktest.infra import logbeamfromlocalhost


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
        nice = 0
        nice = max(nice, float(os.environ.get('RACKTEST_MINIMUM_NICE_FOR_RACKATTACK', 0)))
        return api.AllocationInfo(user=config.USER, purpose="racktest", nice=nice)

    def runOnEveryHost(self, callback, description):
        concurrently.run([
            dict(callback=callback, args=(name,))
            for name in self._nodes])

    def _postMortemAllocation(self):
        try:
            filename, contents = self._allocation.fetchPostMortemPack()
        except:
            logging.exception("Unable to get post mortem pack from rackattack provider")
            return
        tempDir = tempfile.mkdtemp()
        try:
            fullPath = os.path.join(tempDir, filename)
            with codecs.open(fullPath, 'w', 'utf-8') as f:
                f.write(contents)
            logbeamfromlocalhost.beam([fullPath])
        finally:
            shutil.rmtree(tempDir, ignore_errors=True)
        logging.info("Beamed post mortem pack into %(filename)s", dict(filename=filename))
