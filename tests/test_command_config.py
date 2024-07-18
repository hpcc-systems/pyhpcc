import conftest
import pytest
from pyhpcc.command_config import CompileConfig, RunConfig
from pyhpcc.config import (
    MASKED_PASSWORD,
    PASSWORD_OPTIONS,
    PORT_OPTION,
    SERVER_OPTIONS,
    USER_OPTIONS,
)
from pyhpcc.errors import CompileConfigException, RunConfigException
from pyhpcc.models.auth import Auth


@pytest.fixture
def config_option():
    return {"--username": "testuser"}


@pytest.fixture
def auth():
    return Auth("university.hpccsystems.io", "8010", "testuser", "password")


# Test if copy is made out of provided options for creating CompileConfig
def test_compile_config_option_copy(config_option):
    compile_config = CompileConfig(config_option)
    config_option["-dfs"] = "website.com"
    assert compile_config.options != config_option


# Test if compile config validation is not raising exception for correct options
@pytest.mark.parametrize(
    "options",
    [
        {"-user": "testuser"},
        {"-R": "r"},
        {"-Rconfig": "config"},
        {"-f": "feature"},
        {"-fconf": "fconf"},
        {"--updaterepos": bool},
        {"-user": "testuser", "-R": "r", "-fconf": "feature"},
    ],
)
def test_compile_config_validation_no_errors(options):
    compile_config = CompileConfig(options)
    try:
        compile_config.validate_options()
    except CompileConfigException as error:
        pytest.fail(f"Faced with CompileConfig exception {str(error)}")


# Test if CompileConfig validate_options is raising exception for incorrect options
@pytest.mark.parametrize(
    "options",
    [
        {"-u": "testuser"},
        {"--manifest": "r"},
        {"--Rconfig": "config"},
        {"-userd": "testuser", "-R": "r", "-fconf": "feature", "--debug": bool},
    ],
)
def test_compile_config_validation_errors(options):
    compile_config = CompileConfig(options)
    with pytest.raises(CompileConfigException):
        compile_config.validate_options()


# Test if CompileConfig create_compile_bash_command returns correct bash command
@pytest.mark.parametrize(
    "file_name, options, expected_output",
    [
        (
            "abc.xml",
            {"--target": "thor", "-f": "dsafda"},
            "eclcc --target thor -E -f dsafda abc.xml",
        ),
        ("a.xml", {}, "eclcc -E a.xml"),
        (
            "/usr/loc/Basic_job_submission.ecl",
            {
                "-platform": "thor",
                "-wu": bool,
                "-E": bool,
                "-o": "/usr/loc/Basic_job_submission.eclxml",
            },
            "eclcc -platform thor -wu -E -o /usr/loc/Basic_job_submission.eclxml /usr/loc/Basic_job_submission.ecl",
        ),
        (
            "/usr/loc/Basic_job_submission.ecl",
            {
                "-platform": "thor",
                "-wu": bool,
                "-E": bool,
                "-o": "/usr/loc/Basic_job_submission.eclxml",
            },
            "eclcc -platform thor -wu -E -o /usr/loc/Basic_job_submission.eclxml /usr/loc/Basic_job_submission.ecl",
        ),
    ],
)
def test_create_compile_bash_command(file_name, options, expected_output):
    compile_config = CompileConfig(options)
    cmd = compile_config.create_compile_bash_command(file_name)
    assert set(cmd.split(" ")) == set(expected_output.split(" "))


# Test if copy is made out of provided options for creating CompileConfig
def test_run_config_option_copy(config_option):
    run_config = RunConfig(config_option)
    config_option["--v"] = bool
    assert run_config.options != config_option


# Test if RunConfig validate_options is raising exception for incorrect options
@pytest.mark.parametrize(
    "options",
    [
        {"--username": "testuser"},
        {"-X": "x"},
        {"-v": bool},
        {"--verbose": "bool"},
        {"-fconf": "fconf"},
        {"--updaterepos": bool},
        {
            "--username": "testuser",
            "-X": "thor",
            "-fconf": "feature",
            "--fetchrepos": bool,
        },
    ],
)
def test_run_config_validation_no_errors(options):
    run_config = RunConfig(options)
    try:
        run_config.validate_options()
    except RunConfigException as error:
        pytest.fail(f"Faced with CompileConfig exception {str(error)}")


# Test if RunConfig validate_options is raising errors for incorrect options
@pytest.mark.parametrize(
    "options",
    [
        {"--user": "testuser"},
        {"-R": "x"},
        {"--v": bool},
        {"-cacert": "bool"},
        {"-Fconf": "fconf"},
        {"abcd": bool},
        {
            "--user": "testuser",
            "-x": "thor",
            "-Fconf": "feature",
            "--Dname": "name",
        },
    ],
)
def test_run_config_validation_errors(options):
    run_config = RunConfig(options)
    with pytest.raises(RunConfigException):
        run_config.validate_options()


# Test if RunConfig create_run_bash_command is creating correct command
@pytest.mark.parametrize(
    "file_name, options, expected_output",
    [
        (
            "/usr/loc/Basic_job_submission.eclxml",
            {
                "--target": "thor",
                "--job-name": "my_custom_workunit",
                "--limit": 100,
                "-s": conftest.HPCC_HOST,
                "--port": conftest.HPCC_PORT,
                "-u": conftest.HPCC_USERNAME,
                "-pw": conftest.HPCC_PASSWORD,
            },
            f"ecl run /usr/loc/Basic_job_submission.eclxml -v --target thor --job-name my_custom_workunit --limit 100 -s {conftest.HPCC_HOST} --port {conftest.HPCC_PORT} -u {conftest.HPCC_USERNAME} -pw {conftest.HPCC_PASSWORD}",
        ),
        (
            "/usr/loc/Basic_job_submission.eclxml",
            {
                "--target": "thor",
                "--job-name": "Basic_job_submission",
                "--limit": 100,
                "-s": conftest.HPCC_HOST,
                "--port": conftest.HPCC_PORT,
                "-u": conftest.HPCC_USERNAME,
                "-pw": conftest.HPCC_PASSWORD,
            },
            f"ecl run /usr/loc/Basic_job_submission.eclxml -v --target thor --job-name Basic_job_submission --limit 100 -s {conftest.HPCC_HOST} --port {conftest.HPCC_PORT} -u {conftest.HPCC_USERNAME} -pw {conftest.HPCC_PASSWORD}",
        ),
        (
            "/usr/loc/Basic_job_submission.eclxml",
            {
                "--target": "thor",
                "-v": bool,
                "--job-name": "Basic_job_submission",
                "--limit": 100,
                "-s": conftest.HPCC_HOST,
                "--port": conftest.HPCC_PORT,
                "-u": conftest.HPCC_USERNAME,
                "-pw": conftest.HPCC_PASSWORD,
            },
            f"ecl run /usr/loc/Basic_job_submission.eclxml --target thor -v --job-name Basic_job_submission --limit 100 -s {conftest.HPCC_HOST} --port {conftest.HPCC_PORT} -u {conftest.HPCC_USERNAME} -pw {conftest.HPCC_PASSWORD}",
        ),
    ],
)
def test_create_run_bash_command(file_name, options, expected_output):
    run_config = RunConfig(options)
    cmd = run_config.create_run_bash_command(file_name)
    assert set(cmd.split(" ")) == set(expected_output.split(" "))


@pytest.mark.parametrize(
    "file_name, options, expected_output",
    [
        (
            "/usr/loc/Basic_job_submission.eclxml",
            {
                "--target": "thor",
                "--job-name": "my_custom_workunit",
                "--limit": 100,
                "-s": conftest.HPCC_HOST,
                "--port": conftest.HPCC_PORT,
                "-u": conftest.HPCC_USERNAME,
                "-pw": conftest.HPCC_PASSWORD,
            },
            f"ecl run /usr/loc/Basic_job_submission.eclxml -v --target thor --job-name my_custom_workunit --limit 100 -s {conftest.HPCC_HOST} --port {conftest.HPCC_PORT} -u {conftest.HPCC_USERNAME} -pw {MASKED_PASSWORD}",
        ),
    ],
)
def test_create_run_bash_command_mask_password(file_name, options, expected_output):
    run_config = RunConfig(options)
    cmd = run_config.create_run_bash_command(file_name, password_mask=True)
    assert set(cmd.split(" ")) == set(expected_output.split(" "))


# Test if RunConfig create_run_bash_command raises error for incorrect options
@pytest.mark.parametrize(
    "file_name, options",
    [
        (
            "/usr/loc/Basic_job_submission.eclxml",
            {
                "--target": "thor",
                "--name": "Basic_job_submission",
                "--limit": 100,
                "-s": conftest.HPCC_HOST,
                "--port": conftest.HPCC_PORT,
                "-u": conftest.HPCC_USERNAME,
                "-pwd": conftest.HPCC_PASSWORD,
            },
        ),
    ],
)
def test_create_run_bash_command_errors(file_name, options):
    run_config = RunConfig(options)
    with pytest.raises(RunConfigException):
        run_config.create_run_bash_command(file_name)


# Test RunConfig set_auth_params set the auth options properly
def test_set_auth_params(config_option, auth: Auth):
    run_config = RunConfig(config_option)
    run_config.set_auth_params(auth)
    assert run_config.get_option(SERVER_OPTIONS[0]) == auth.ip
    assert run_config.get_option(PASSWORD_OPTIONS[0]) == auth.password
    assert run_config.get_option(PORT_OPTION) == auth.port
    assert run_config.get_option(USER_OPTIONS[0]) == auth.username
    assert len(run_config.options) == 4
