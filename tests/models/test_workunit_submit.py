import copy
import os
import subprocess

import config
import pytest
from pyhpcc.command_config import CompileConfig
from pyhpcc.config import OUTPUT_FILE_OPTION
from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC
from pyhpcc.models.workunit_submit import WorkunitSubmit

DUMMY_OUTPUT = "dummy_output"

HPCC_HOST = config.HPCC_HOST
HPCC_PASSWORD = config.HPCC_PASSWORD
HPCC_PORT = config.HPCC_PORT
HPCC_USERNAME = config.HPCC_USERNAME
ENV = "LOCAL"


@pytest.fixture
def auth():
    return Auth(HPCC_HOST, HPCC_PORT, HPCC_USERNAME, HPCC_PASSWORD)


@pytest.fixture
def hpcc(auth):
    return HPCC(auth)


@pytest.fixture
def clusters():
    return ("thor", "hthor")


@pytest.fixture
def ws(hpcc, clusters):
    return WorkunitSubmit(hpcc, clusters)


# Test if creation of WorkUnitSubmit raises error if no clusters are provided
def test_work_unit_creation_error(hpcc):
    with pytest.raises(ValueError):
        WorkunitSubmit(hpcc, ())


# Test WorkUnitSubmit creation with correct parameters
def test_work_unit_creation_noerror(hpcc, clusters):
    try:
        WorkunitSubmit(hpcc, clusters)
    except Exception as error:
        pytest.fail(
            f"Faced with exception while creating WorkunitSubmit object {str(error)}"
        )


# Test if get_bash_command produces correct output with and without output file in CompileConfig
@pytest.mark.parametrize(
    "config, input_file, expected_output",
    [
        ({}, "a.ecl", ("eclcc -o a.eclxml a.ecl", "a.eclxml")),
        (
            {OUTPUT_FILE_OPTION: "hello.eclxml"},
            "a.ecl",
            ("eclcc -o hello.eclxml a.ecl", "hello.eclxml"),
        ),
    ],
)
def test_get_bash_command_output_file(ws, config, input_file, expected_output):
    compile_config = CompileConfig(config)
    assert expected_output == ws.get_bash_command(input_file, compile_config)


class MockProcess:
    def communicate(*args, **kwargs):
        return (DUMMY_OUTPUT, "dummy_error")


# Test WorkunitSubmit bash_compile with mocking compile method
@pytest.mark.parametrize(
    "config, input_file, expected_output",
    [
        ({}, "a.ecl", (DUMMY_OUTPUT, "a.eclxml")),
        (
            {OUTPUT_FILE_OPTION: "hello.eclxml"},
            "a.ecl",
            (DUMMY_OUTPUT, "hello.eclxml"),
        ),
    ],
)
def test_bash_compile(config, input_file, expected_output, monkeypatch, ws):
    def dummy_process(*args, **kwargs):
        return MockProcess()

    monkeypatch.setattr(subprocess, "Popen", dummy_process)
    output = ws.bash_compile(input_file, config)
    assert output == expected_output


activity_response_skeleton = {"ActivityResponse": {"Running": {"ActiveWorkunit": []}}}


def create_tests():
    active_workunits = {
        ("thor", "hthor", "thor", "dthor"): "hthor",
        ("dthor", "thor"): "hthor",
        ("dthor", "hthor", "hthor", "thor"): "thor",
    }
    inputs = []
    for resp_clusters, answer in active_workunits.items():
        temp = []
        for cluster in resp_clusters:
            temp.append({"TargetClusterName": cluster})
        input = copy.deepcopy(activity_response_skeleton)
        input["ActivityResponse"]["Running"]["ActiveWorkunit"] = temp
        inputs.append((input, answer))
    return inputs


# Test if WorkunitSubmit get_cluster_from_response cluster selection is correct from Activity API response
@pytest.mark.parametrize("activity, expected_output", create_tests())
def test_get_cluster_from_response(activity, expected_output, ws):
    output = ws.get_cluster_from_response(activity)
    assert output == expected_output


# Test if get_least_active_cluster return least active cluster directly returns if only one cluster is configured
def test_get_cluster_when_one_cluster(hpcc):
    clusters = ("thor",)
    ws = WorkunitSubmit(hpcc, clusters)
    ws.get_least_active_cluster() == clusters[0]


# Test if file is created with the contents for create_file_name function
@pytest.mark.parametrize(
    "content, job_name, expected_file",
    [("OUTPUT('HELLO WORLD!');", "Basic Job", "Basic_Job.ecl")],
)
def test_create_file(tmp_path, ws, content, job_name, expected_file):
    output = ws.create_file_name(content, tmp_path, job_name)
    ecl_file_path = tmp_path / expected_file
    assert output == str(ecl_file_path)
    assert ecl_file_path.read_text() == content


# Test if compilation is working for bash_compile: Runs only in local
@pytest.mark.skipif(
    config.ENV != "LOCAL",
    reason="ECL Client Tools required. Can't run on github runner",
)
@pytest.mark.parametrize(
    "job_name, expected_file, options, content, error_code",
    [
        ("Basic Job", "Basic_job.eclxml", {"-E": True}, "OUTPUT('HELLO WORLD!');", -1),
        # ("Basic Job", "Basic_job.eclxml", {"-E": True}, "OUTPUT('HELLO WORL", 185),
        ("Basic Job", "Basic_job.eclxml", None, "OUTPUT('HELLO WORLD!');", -1),
    ],
)
def test_bash_compile_full(
    tmp_path, ws, job_name, options, expected_file, content, error_code
):
    output_file = ws.create_file_name(content, tmp_path, job_name)
    output, error = ws.bash_compile(output_file, options)
    assert os.path.exists(tmp_path / expected_file)
    assert str(output).find("error") == error_code


# Test if RunConfig options are properly instantiated.
@pytest.mark.parametrize(
    "options, expected_options",
    [
        (
            None,
            {
                "--target": "thor",
                "--name": "Basic_Job",
                "--limit": 100,
                "-s": HPCC_HOST,
                "--port": f"{HPCC_PORT}",
                "-u": HPCC_USERNAME,
                "-pw": HPCC_PASSWORD,
            },
        ),
        (
            {"--target": "hthor", "--limit": 1000, "--name": "Basic Job 2"},
            {
                "--target": "hthor",
                "--name": "Basic Job 2",
                "--limit": 1000,
                "-s": HPCC_HOST,
                "--port": f"{HPCC_PORT}",
                "-u": HPCC_USERNAME,
                "-pw": HPCC_PASSWORD,
            },
        ),
    ],
)
def test_configure_run_config(hpcc, options, expected_options):
    clusters = ("thor",)
    ws = WorkunitSubmit(hpcc, clusters)
    ws.job_name = "Basic Job"
    run_config = ws.configure_run_config(options)
    assert run_config.options == expected_options
