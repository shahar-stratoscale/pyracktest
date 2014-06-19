from strato.racktest.infra import config
from strato.racktest.infra import executioner
from strato.common.log import configurelogging
import logging
import os
import shutil
from strato.common import log
import imp


def runSingleScenario(scenarioFilename):
    testName = os.path.splitext(scenarioFilename)[0].replace('/', '.')
    _configureTestLogging(testName)
    logging.info("Running '%(scenarioFilename)s' as a test class", dict(scenarioFilename=scenarioFilename))
    try:
        module = imp.load_source('test', scenarioFilename)
        execute = executioner.Executioner(module.Test)
        execute.executeTestScenario()
    except:
        logging.exception(
            "Failed running '%(scenarioFilename)s' as a test class",
            dict(scenarioFilename=scenarioFilename))
        logging.shutdown()
        raise
    finally:
        logging.info(
            "Done Running '%(scenarioFilename)s' as a test class",
            dict(scenarioFilename=scenarioFilename))
        logging.shutdown()


def _configureTestLogging(testName):
    dirPath = os.path.join(config.TEST_LOGS_DIR, testName)
    shutil.rmtree(dirPath, ignore_errors=True)
    configurelogging.configureLogging('test', forceDirectory=dirPath)


if __name__ == "__main__":
    import sys
    config.load(sys.argv[1])
    runSingleScenario(sys.argv[2])
