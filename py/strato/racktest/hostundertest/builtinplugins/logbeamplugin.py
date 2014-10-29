from strato.racktest.hostundertest import plugins
from strato.racktest.infra import logbeamfromlocalhost
import os
import socket
import shutil
import string
import tempfile
import codecs


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
        self._postMortemCommands()
        self.postMortemSerial()

    def _postMortemCommands(self):
        script = "\n".join(
            "%s < /dev/null >& /tmp/postmortem/%s" % (command, self._safeFilename(command))
            for command in POST_MORTEM_COMMANDS)
        self._host.ssh.run.script('mkdir /tmp/postmortem\n%s\n' % script)
        self.beam("/tmp/postmortem", under="postmortem")

    def postMortemSerial(self):
        serialFilePath = self._saveSerial()
        logbeamfromlocalhost.beam([serialFilePath], under=os.path.join(self._host.name, "postmortem"))
        shutil.rmtree(os.path.dirname(serialFilePath), ignore_errors=True)

    def _saveSerial(self):
        serialContent = self._host.node.fetchSerialLog()
        tempDir = tempfile.mkdtemp()
        serialFilePath = os.path.join(tempDir, "serial.txt")
        self._writeUnicodeFile(serialContent, serialFilePath)
        return serialFilePath

    def _safeFilename(self, unsafe):
        SAFE = string.ascii_letters + string.digits
        return "".join(c if c in SAFE else '_' for c in unsafe)

    def _configure(self):
        config = logbeamfromlocalhost.logbeamConfigurationForPeer(
            self._myIPForHost(), under=self._host.name)
        self._host.ssh.ftp.putContents("/etc/logbeam.config", config)
        self._configured = True

    def _myIPForHost(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect((self._host.node.ipAddress(), 1))
            return s.getsockname()[0]
        finally:
            s.close()

    def _writeUnicodeFile(self, content, filePath):
        with codecs.open(filePath, 'w', 'utf-8') as f:
            f.write(content)


plugins.register('logbeam', LogBeamPlugin)
