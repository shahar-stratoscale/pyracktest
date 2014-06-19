from strato.racktest.hostundertest import plugins
import os
import time


class RPM:
    def __init__(self, host):
        self._host = host

    def installRPMPackage(self, path):
        basename = os.path.basename(path)
        self._host.ssh.ftp.putFile(basename, path)
        self._retryInstallPackageSinceAtBootTimeMightBeLocked(basename)

    def _retryInstallPackageSinceAtBootTimeMightBeLocked(self, basename):
        RETRIES = 20
        for i in xrange(RETRIES):
            try:
                self._host.ssh.run.script("rpm -i --force ./%s" % basename)
                return
            except Exception as e:
                if i < RETRIES - 1 and 'yum status database is locked by another process' in str(e):
                    time.sleep(0.5)
                    continue
                raise


plugins.register('rpm', RPM)
