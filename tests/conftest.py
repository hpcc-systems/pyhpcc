import os

import pytest
from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC
from pyhpcc.models.workunit_submit import WorkunitSubmit


class DUMMY_SECRETS:
    HPCC_USERNAME = ""
    HPCC_PASSWORD = ""
    DUMMY_USERNAME = ""
    DUMMY_PASSWORD = ""
    HPCC_HOST = ""
    HPCC_PORT = 0
    HPCC_PROTOCOL = ""
    DUMMY_HPCC_HOST = ""
    DUMMY_HPCC_PORT = 0
    ENV = "LOCAL"
    LANDING_ZONE_IP = ""
    LANDING_ZONE_PATH = ""
    DFU_CLUSTER = ""


try:
    import my_secret
except Exception:
    my_secret = DUMMY_SECRETS
ENV_VAR = "ENV"
## HPCC Config
HPCC_USERNAME = os.environ.get("HPCC_USERNAME") or my_secret.HPCC_USERNAME
HPCC_PASSWORD = os.environ.get("HPCC_PASSWORD") or my_secret.HPCC_PASSWORD
DUMMY_USERNAME = os.environ.get("DUMMY_USERNAME") or my_secret.DUMMY_USERNAME
DUMMY_PASSWORD = os.environ.get("DUMMY_PASSWORD") or my_secret.DUMMY_PASSWORD
HPCC_HOST = os.environ.get("HPCC_HOST") or my_secret.HPCC_HOST
HPCC_PORT = os.environ.get("HPCC_PORT") or my_secret.HPCC_PORT
HPCC_PROTOCOL = os.environ.get("HPCC_PROTOCOL") or my_secret.HPCC_PROTOCOL
DUMMY_HPCC_HOST = os.environ.get("DUMMY_HPCC_HOST") or my_secret.DUMMY_HPCC_HOST
DUMMY_HPCC_PORT = os.environ.get("DUMMY_HPCC_PORT") or my_secret.DUMMY_HPCC_PORT
ENV = os.environ.get(ENV_VAR) or my_secret.ENV
LANDING_ZONE_IP = os.environ.get("LANDING_ZONE_IP") or my_secret.LANDING_ZONE_IP
LANDING_ZONE_PATH = os.environ.get("LANDING_ZONE_PATH") or my_secret.LANDING_ZONE_PATH
DFU_CLUSTER = os.environ.get("DFU_CLUSTER") or my_secret.DFU_CLUSTER


@pytest.fixture(scope="session")
def hpcc_host():
    return HPCC_HOST


@pytest.fixture(scope="session")
def hpcc_port():
    return HPCC_PORT


@pytest.fixture(scope="session")
def hpcc_username():
    return HPCC_USERNAME


@pytest.fixture(scope="session")
def hpcc_password():
    return HPCC_PASSWORD


@pytest.fixture(scope="session")
def hpcc_protocol():
    return HPCC_PROTOCOL


@pytest.fixture(scope="session")
def dummy_username():
    return DUMMY_USERNAME


@pytest.fixture(scope="session")
def dummy_password():
    return dummy_password


@pytest.fixture(scope="session")
def dummy_hpcc_host():
    return DUMMY_HPCC_HOST


@pytest.fixture(scope="session")
def dummy_hpcc_port():
    return DUMMY_HPCC_PORT


@pytest.fixture(scope="session")
def auth(hpcc_host, hpcc_port, hpcc_username, hpcc_password, hpcc_protocol):
    return Auth(
        hpcc_host, hpcc_port, hpcc_username, hpcc_password, protocol=hpcc_protocol
    )


@pytest.fixture(scope="session")
def hpcc(auth):
    return HPCC(auth)


@pytest.fixture
def ws(hpcc, clusters):
    return WorkunitSubmit(hpcc, clusters)


@pytest.fixture(scope="session")
def flat_file():
    return "pyhpcc::employee::dummy::thor"


@pytest.fixture(scope="session")
def logical_file():
    return "pyhpcc::employee::dummy::thor"


@pytest.fixture(scope="session")
def csv_file():
    return "pyhpcc::employee::dummy::data"


@pytest.fixture(scope="session")
def super_file():
    return "class::mdm::sf::alldata"


@pytest.fixture(scope="session")
def landing_zone_ip():
    return LANDING_ZONE_IP


@pytest.fixture(scope="session")
def landing_zone_path():
    return LANDING_ZONE_PATH


@pytest.fixture(scope="session")
def dfu_cluster():
    return DFU_CLUSTER
