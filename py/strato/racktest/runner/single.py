from strato.racktest.infra import config
from strato.racktest.infra import executioner
from strato.common.log import configurelogging
import logging
import os
import shutil
from strato.common import log
import imp


def runSingleScenario(scenarioFilename, instance, allocation_timeout):
    testName = os.path.splitext(scenarioFilename)[0].replace('/', '.')
    _configureTestLogging(testName + instance)
    logging.info("Running '%(scenarioFilename)s' as a test class (instance='%(instance)s')", dict(
        scenarioFilename=scenarioFilename, instance=instance))
    try:
        module = imp.load_source('test', scenarioFilename)
        execute = executioner.Executioner(module.Test)
        execute.executeTestScenario(allocation_timeout=allocation_timeout)
    except:
        logging.exception(
            "Failed running '%(scenarioFilename)s' as a test class (instance='%(instance)s')",
            dict(scenarioFilename=scenarioFilename, instance=instance))
        logging.shutdown()
        raise
    finally:
        logging.info(
            "Done Running '%(scenarioFilename)s' as a test class (instance='%(instance)s')",
            dict(scenarioFilename=scenarioFilename, instance=instance))
        logging.shutdown()


def _configureTestLogging(testName):
    dirPath = os.path.join(config.TEST_LOGS_DIR, testName)
    shutil.rmtree(dirPath, ignore_errors=True)
    configurelogging.configureLogging('test', forceDirectory=dirPath)


if __name__ == "__main__":
    import sys
    config.load(sys.argv[1])
    runSingleScenario(sys.argv[2],
                      sys.argv[3],
                      allocation_timeout=int(sys.argv[4]))
