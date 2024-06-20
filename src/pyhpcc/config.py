# Configurations for pyhpcc
import os

## Debug Config
# If the debug env variable exists, set to False else set to True
DEBUG = os.environ.get("DEBUG", False) or True

## Workunit Config
WORKUNIT_STATE_MAP = {
    "unknown": 0,
    "compiled": 1,
    "running": 2,
    "completed": 3,
    "failed": 4,
    "archived": 5,
    "aborting": 6,
    "aborted": 7,
    "blocked": 8,
    "submitted": 9,
    "scheduled": 10,
    "compiling": 11,
    "wait": 12,
    "uploadingFiles": 13,
    "debugPaused": 14,
    "debugRunning": 15,
    "paused": 16,
    "statesize": 17,
}


platforms = {"hthor", "thor", "roxie"}

DEFAULT_COMPILE_OPTIONS = {"-platform": "thor", "-wu": True, "-E": True}
DEFUALT_RUN_OPTIONS = {}

CLUSTER_PARAM = "--target"
JOB_NAME_PARAM = "--name"
LIMIT_PARAM = "--limit"
DEFAULT_LIMIT = 100
USER_OPTIONS = ["-u", "--username"]
PASSWORD_OPTIONS = ["-pw", "--password"]
SERVER_OPTIONS = ["-s", "--s"]
PORT_OPTION = ["--port"]
VERBOSE_OPTIONS = [
    "-v",
    "--verbose",
]
RUN_AUTH_OPTIONS = {*USER_OPTIONS, *PASSWORD_OPTIONS, *SERVER_OPTIONS, *PORT_OPTION}

COMPILE_OPTIONS = {
    "-I",
    "-L",
    "-o",
    "-manifest",
    "--main",
    "-syntax",
    "-platform",
    "-E",
    "-q",
    "-qa",
    "-wu",
    "-S",
    "-g",
    "--debug",
    "-Wc",
    "-xx",
    "-shared",
    "-dfs",
    "-scope",
    "-cluster",
    "-user",
    "-password",
    "-checkDirty",
    "--cleanrepos",
    "--cleaninvalidrepos",
    "--fetchrepos",
    "-help",
    "--help",
    "--logfile",
    "--metacache",
    "--nosourcepath",
    "-specs",
    "--updaterepos",
    *VERBOSE_OPTIONS,
    "-wxxxx",
    "--version",
    CLUSTER_PARAM,
}

RUN_OPTIONS = {
    "--job-name",
    "--input",
    "-in",
    "--wait",
    "--poll",
    "--exception-level",
    "--protect",
    "--main",
    "--snapshot",
    "--ecl-only",
    "--limit",
    "-Dname",
    "-I",
    "-L",
    "-manifest",
    "-g",
    "debug",
    "--checkDirty",
    "--cleanrepos",
    "--cleaninvalidrepos",
    "--fetchrepos",
    "--updaterepos",
    "--help",
    *SERVER_OPTIONS,
    "--ssl",
    "-ssl",
    "--accept-self-signed",
    "--cert",
    "--key",
    "--cacert",
    *PORT_OPTION,
    *USER_OPTIONS,
    *PASSWORD_OPTIONS,
    "--wait-connect",
    "--wait-read",
    CLUSTER_PARAM,
    JOB_NAME_PARAM,
    *VERBOSE_OPTIONS,
}
