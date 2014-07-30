from strato.racktest.hostundertest import plugins
import os
import time
import socket


class RPM:
    def __init__(self, host):
        self._host = host

    def installRPMPackage(self, path):
        basename = os.path.basename(path)
        self._host.ssh.ftp.putFile(basename, path)
        self._retryInstallPackageSinceAtBootTimeMightBeLocked(basename)

    def yumInstall(self, packageList):
        if isinstance(packageList, str):
            packageList = [packageList]
        self._host.ssh.run.script("yum install %s --assumeyes" % (" ".join(packageList)))

    def makeYUMCachePointToTestRunner(self):
        ip = self._myIPForHost()
        self._host.ssh.run.script("sed -i 's/127.0.0.1/%s/' /etc/yum.conf" % ip)

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

    def _myIPForHost(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((self._host.node.ipAddress(), 1))
            return s.getsockname()[0]
        finally:
            s.close()


plugins.register('rpm', RPM)
