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

DEFAULT_COMPILE_OPTIONS = {"-platform": "thor", "-wu": bool, "-E": bool}
DEFUALT_RUN_OPTIONS = {}

COMMAND = "command"
CLUSTER_OPTION = "--target"
JOB_NAME_OPTION = "--job-name"
LIMIT_OPTION = "--limit"
DEFAULT_LIMIT = 100
USER_OPTIONS = ["-u", "--username"]
PASSWORD_OPTIONS = ["-pw", "--password"]
SERVER_OPTIONS = ["-s", "--s"]
PORT_OPTION = "--port"
OUTPUT_FILE_OPTION = "-o"
OUTPUT_XML = "-E"
VERBOSE_OPTIONS = [
    "-v",
    "--verbose",
]
RUN_UNWANTED_PATTERNS = [
    r"jsocket\([0-9]+,[0-9]+\) ",
    "deploying",
    "Deployed",
    "Running",
    "Using eclcc path ",
]
MASKED_PASSWORD = "*****"
RUN_AUTH_OPTIONS = {*USER_OPTIONS, *PASSWORD_OPTIONS, *SERVER_OPTIONS, PORT_OPTION}

COMPILE_OPTIONS = {
    "-I",
    "-L",
    "-manifest",
    "--main",
    "-syntax",
    "-platform",
    OUTPUT_XML,
    "-q",
    "-qa",
    "-wu",
    "-dfs",
    "-scope",
    "-cluster",
    "-user",
    "-password",
    "-checkDirty",
    "--cleanrepos",
    "--cleaninvalidrepos",
    "--fetchrepos",
    "--logfile",
    "--metacache",
    "--nosourcepath",
    "-specs",
    "--updaterepos",
    *VERBOSE_OPTIONS,
    "-wxxxx",
    "--version",
    "--help",
    CLUSTER_OPTION,
    OUTPUT_FILE_OPTION,
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
    PORT_OPTION,
    *USER_OPTIONS,
    *PASSWORD_OPTIONS,
    "--wait-connect",
    "--wait-read",
    CLUSTER_OPTION,
    JOB_NAME_OPTION,
    *VERBOSE_OPTIONS,
}


RUN_ERROR_MSG_PATTERN = [
    "401: Unauthorized",
    "Error checking ESP configuration",
    "Bad host name/ip:",
]

COMPILE_ERROR_MIDDLE_PATTERN = [
    r"\(\d+,\d+\): error C([0-9]){3,6}",
]

COMPILE_ERROR_PATTERN = [
    "Error: ",
    "Failed to compile ",
]
FAILED_STATUS = {"failed", "aborted", "aborting"}

WUID_PATTERN = "^(wuid): (W[0-9]+-[0-9]+)$"
WUID = "wuid"
STATE_PATTERN = f"^(state): ({"|".join(WORKUNIT_STATE_MAP.keys())})$"
STATE = "state"
