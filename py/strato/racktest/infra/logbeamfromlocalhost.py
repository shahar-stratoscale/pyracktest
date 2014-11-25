import os
import threading
import logbeam.config
import logbeam.upload
import logbeam.ftpserver
import subprocess
import logging
import time
import socket
from strato.common import log


_server = None
_serverLock = threading.Lock()
_configured = False
_configuredLock = threading.Lock()
_previousLogbeamConfigExisted = None
_FTP_USERNAME = 'logs'
_FTP_PASSWORD = 'logs'


def beam(*args, **kwargs):
    _configureBeamFromLocal()
    logbeam.upload.Upload().upload(*args, **kwargs)


def logbeamConfigurationForPeer(myHostnameAsPeerSeesIt, under):
    _configureBeamFromLocal()
    assert _previousLogbeamConfigExisted is not None
    if _previousLogbeamConfigExisted:
        return subprocess.check_output(["logbeam", "createConfig", "--under", under])
    else:
        return (
            "HOSTNAME: %s\nUSERNAME: %s\nPASSWORD: %s\nPORT: %d\nUPLOAD_TRANSPORT: ftp\n"
            "BASE_DIRECTORY: '%s'\n") % (
                myHostnameAsPeerSeesIt, _FTP_USERNAME, _FTP_PASSWORD, _server.actualPort(), under)


def _configureBeamFromLocal():
    global _configured
    global _configuredLock
    global _previousLogbeamConfigExisted
    global _server
    with _configuredLock:
        if _configured:
            return
        _configured = True
        logbeam.config.load()
        _previousLogbeamConfigExisted = logbeam.config.UPLOAD_TRANSPORT != "null"
        if _previousLogbeamConfigExisted:
            return
        _server = logbeam.ftpserver.FTPServer(
            directory=log.config.LOGS_DIRECTORY, port=0,
            username=_FTP_USERNAME, password=_FTP_PASSWORD)
        logging.getLogger('pyftpdlib').setLevel(logging.WARNING)
        config = (
            "HOSTNAME: localhost\nUSERNAME: %s\nPASSWORD: %s\nPORT: %d\n"
            "UPLOAD_TRANSPORT: ftp\n") % (
                _FTP_USERNAME, _FTP_PASSWORD, _server.actualPort())
        os.environ['LOGBEAM_CONFIG'] = config
        logbeam.config.load()
        _waitForLocalhostTCPServer(_server.actualPort())


def _waitForLocalhostTCPServer(port, timeout=5, interval=0.1):
    before = time.time()
    while time.time() - before < timeout:
        if _rawTCPConnect(('localhost', port)):
            return
        time.sleep(interval)
    raise Exception("Logbeam ftp server 'localhost:%s' did not respond within timeout" % port)


def _rawTCPConnect(tcpEndpoint):
    s = socket.socket()
    try:
        s.connect(tcpEndpoint)
        return True
    except:
        return False
    finally:
        s.close()
