from strato.racktest.hostundertest import plugins
import socket
import threading
import logbeam.config
import logbeam.ftpserver
import subprocess
import string
from strato.common import log


_server = None
_serverLock = threading.Lock()
_logbeamConfigurationLoaded = False
_logbeamConfigurationLoadedLock = threading.Lock()

# append to this if you have special needs
POST_MORTEM_COMMANDS = [
    'id',
    'date "+%Y-%m-%d %H:%M:%S.%N"',
    'ps -Af --forest',
    'top -wbcn 1',
    'ip addr',
    'ip route',
    'brctl show',
    'brctl showmacs br100',
    'ifconfig -a',
    'route -n',
    'lsmod',
    'df',
    'free',
    'lspci',
    'lsof',
    'netstat -nlp',
    'netstat -neap']


class LogBeamPlugin:
    _FTP_USERNAME = 'logs'
    _FTP_PASSWORD = 'logs'

    def __init__(self, host):
        self._host = host
        self._configured = False

    def beam(self, *sources, **kwargs):
        under = kwargs.get('under', None)
        self._configure()
        self._host.seed.runCode(
            "import logbeam.upload\n"
            "logbeam.config.load()\n"
            "logbeam.upload.Upload().upload(%s, under=%s)\n" % (
                sources, 'None' if under is None else "'%s'" % under),
            takeSitePackages=True)

    def postMortem(self):
        script = "\n".join(
            "%s < /dev/null >& /tmp/postmortem/%s" % (command, self._safeFilename(command))
            for command in POST_MORTEM_COMMANDS)
        self._host.ssh.run.script('mkdir /tmp/postmortem\n%s\n' % script)
        self.beam("/tmp/postmortem", under="postmortem")

    def _safeFilename(self, unsafe):
        SAFE = string.ascii_letters + string.digits
        return "".join(c if c in SAFE else '_' for c in unsafe)

    def _configure(self):
        if self._configured:
            return
        with _logbeamConfigurationLoadedLock:
            global _logbeamConfigurationLoaded
            if not _logbeamConfigurationLoaded:
                logbeam.config.load()
                _logbeamConfigurationLoaded = True
        if self._logbeamPreviouslyConfiguredWithDestination():
            config = subprocess.check_output(["logbeam", "createConfig", "--under", self._host.name])
        else:
            self._startServer()
            config = (
                "HOSTNAME: %s\nUSERNAME: %s\nPASSWORD: %s\nPORT: %d\nUPLOAD_TRANSPORT: ftp\n"
                "BASE_DIRECTORY: '%s'\n") % (
                    self._myIPForHost(), self._FTP_USERNAME, self._FTP_PASSWORD,
                    _server.actualPort(), self._host.name)
        self._host.ssh.ftp.putContents("/etc/logbeam.config", config)
        self._configured = True

    def _logbeamPreviouslyConfiguredWithDestination(self):
        return logbeam.config.UPLOAD_TRANSPORT != "null"

    def _myIPForHost(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((self._host.node.ipAddress(), 1))
            return s.getsockname()[0]
        finally:
            s.close()

    def _startServer(self):
        global _server
        global _serverLock
        with _serverLock:
            if _server is not None:
                return
            _server = logbeam.ftpserver.FTPServer(
                directory=log.config.LOGS_DIRECTORY, port=0,
                username=self._FTP_USERNAME, password=self._FTP_PASSWORD)


plugins.register('logbeam', LogBeamPlugin)
