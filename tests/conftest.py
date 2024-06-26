import os


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
    WUID = ""
    DEBUG = False
    ENV = "LOCAL"


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
WUID = os.environ.get("WUID") or my_secret.WUID
ENV = os.environ.get(ENV_VAR) or my_secret.ENV
