import logging

from pyhpcc.config import (
    CLUSTER_OPTION,
    COMPILE_OPTIONS,
    JOB_NAME_OPTION,
    LIMIT_OPTION,
    MASKED_PASSWORD,
    OUTPUT_FILE_OPTION,
    PASSWORD_OPTIONS,
    PORT_OPTION,
    RUN_AUTH_OPTIONS,
    RUN_OPTIONS,
    SERVER_OPTIONS,
    USER_OPTIONS,
)
from pyhpcc.errors import CompileConfigException, RunConfigException
from pyhpcc.models.auth import Auth

log = logging.getLogger(__name__)


class CompileConfig(object):
    """
    Class for eclcc option configuration

    Attributes:
    ----------
        options:
            Dictionary of keys (option), values (value)

    Methods:
    -------
        validate_options:
            Validate if the compiler options are supported or not

        set_output_file:
            Set name of output file (default a.out if linking to

        create_compile_bash_command:
            Generate the eclcc command for the given options and input_file

        get_option:
            Retrieves the compile config option


    """

    def __init__(self, options: dict):
        self.options = options.copy()

    def validate_options(self):
        """Validate if the compiler options are supported or not"""
        invalid_options = []
        for option in self.options:
            if option not in COMPILE_OPTIONS and not (
                option.startswith("-R") or option.startswith("-f")
            ):
                invalid_options.append(option)
        if len(invalid_options) > 0:
            raise CompileConfigException(str(invalid_options))

    def set_output_file(self, output_file):
        """Set name of output file (default a.out if linking to"""
        self.options[OUTPUT_FILE_OPTION] = output_file

    def create_compile_bash_command(self, input_file):
        """Generate the eclcc command for the given options and input_file"""
        self.validate_options()
        eclcc_command = "eclcc"
        for key, value in self.options.items():
            if value is bool:
                eclcc_command += f" {key}"
            else:
                eclcc_command += f" {key} {value}"
        eclcc_command = f"{eclcc_command} {input_file}"
        return eclcc_command

    def get_option(self, option):
        """Get the option available for the option"""
        return self.options[option]


class RunConfig(object):
    """
    Class for ecl run option configuration

    Attributes:
    ----------
        options:
            Dictionary of keys (option), values (value)

    Methods:
    -------
        validate_options:
            Validate if the compiler options are supported or not

        create_run_bash_command:
            Generate the ecl command for the given options and target_file

        set_auth_params:
            Set the auth parameters from the auth object passed

        set_target:
            Specify the job name for the workunit

        set_limit:
            Sets the result limit for the query

        set_server:
            Set IP of server running ecl services (eclwatch)

        set_port:
            Set ECL services port

        set_username:
            Set username for accessing ecl services

        set_password:
            Set password for accessing ecl services

        get_option:
            Retrieves the run config option

    """

    def __init__(self, options: dict):
        self.options = options.copy()

    def validate_options(self):
        """Validate if the runtime options are supported or not"""
        invalid_options = set()
        for option in self.options:
            if option not in RUN_OPTIONS and not (
                option.startswith("-X") or option.startswith("-f")
            ):
                invalid_options.add(option)
        if len(invalid_options) > 0:
            log.error("Entered invalid options %s", str(invalid_options))
            raise RunConfigException(
                f"Invalid options not supported by pyhpcc {str(invalid_options)}"
            )

    def create_run_bash_command(self, target_file, password_mask=False):
        """Generate the ecl command for the given options and target_file"""
        self.validate_options()
        ecl_command = "ecl run"
        params = ""
        for key, value in self.options.items():
            if value is bool:
                params += f" {key}"
            else:
                if key in PASSWORD_OPTIONS and password_mask:
                    params += f" {key} {MASKED_PASSWORD}"
                else:
                    params += f" {key} {value}"
        ecl_command = f"{ecl_command} {target_file}{params}"
        log.info(ecl_command)
        return ecl_command

    def set_auth_params(self, auth: Auth):
        """Set the auth parameters from the auth object passed"""
        for option in list(self.options):
            if option in RUN_AUTH_OPTIONS:
                log.warning(f"Overriding option {option} with Auth object parameters")
                del self.options[option]
        self.set_server(auth.ip)
        self.set_port(auth.port)
        self.set_username(auth.oauth[0])
        self.set_password(auth.oauth[1])

    def set_target(self, target):
        """Set the target"""
        self.options[CLUSTER_OPTION] = target

    def set_job_name(self, job_name):
        """Specify the job name for the workunit"""
        self.options[JOB_NAME_OPTION] = job_name

    def set_limit(self, limit):
        """Sets the result limit for the query"""
        self.options[LIMIT_OPTION] = limit

    def set_server(self, server):
        """Set IP of server running ecl services (eclwatch)"""
        self.options[SERVER_OPTIONS[0]] = server

    def set_port(self, port):
        """Set ECL services port"""
        self.options[PORT_OPTION] = port

    def set_username(self, username):
        """Set username for accessing ecl services"""
        self.options[USER_OPTIONS[0]] = username

    def set_password(self, password):
        """Set password for accessing ecl services"""
        self.options[PASSWORD_OPTIONS[0]] = password

    def get_option(self, option):
        """Get the option available for the option"""
        return self.options[option]
