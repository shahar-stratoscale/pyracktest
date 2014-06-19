import yaml

USER = None
TEST_LOGS_DIR = "logs.racktest"


def load(filename="/etc/racktest.conf"):
    with open(filename) as f:
        data = yaml.load(f.read())
    if data is None:
        raise Exception("Configuration file must not be empty")
    globals().update(data)
    if USER is None:
        raise Exception("Configuration file must contain 'USER' field")
