import copy
import os

import conftest
import pytest
from pyhpcc.command_config import CompileConfig
from pyhpcc.config import ECL_OUTPUT_DIR, OUTPUT_FILE_OPTION
from pyhpcc.models.workunit_submit import WorkunitSubmit

DUMMY_OUTPUT = "dummy_output"

HPCC_HOST = conftest.HPCC_HOST
HPCC_PASSWORD = conftest.HPCC_PASSWORD
HPCC_PORT = conftest.HPCC_PORT
HPCC_USERNAME = conftest.HPCC_USERNAME


@pytest.fixture
def clusters():
    return ("thor", "hthor")


@pytest.fixture
def ecl_output_dir():
    return "ecl-output"


@pytest.fixture
def ecl_hello_query():
    return "OUTPUT('HELLO WORLD!');"


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
        ({}, "a.ecl", ("eclcc -E -o a.eclxml a.ecl", "a.eclxml")),
        (
            {OUTPUT_FILE_OPTION: "hello.eclxml"},
            "a.ecl",
            ("eclcc -o hello.eclxml -E a.ecl", "hello.eclxml"),
        ),
    ],
)
def test_get_bash_command_output_file(ws, config, input_file, expected_output):
    compile_config = CompileConfig(config)
    bash_command, output_file = ws.get_bash_command(input_file, compile_config)
    assert set(bash_command.split(" ")) == set(expected_output[0].split(" "))
    assert output_file == expected_output[1]


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
def test_create_file(tmpdir, ws, content, job_name, expected_file):
    working_directory = tmpdir
    output = ws.create_file_name(content, working_directory, job_name)
    ecl_file_path = os.path.join(working_directory, ECL_OUTPUT_DIR, expected_file)
    assert output == str(ecl_file_path)
    assert open(ecl_file_path, "r").read() == content


# Test if compilation is working for bash_compile: Runs only in local
@pytest.mark.skipif(
    conftest.ENV != "LOCAL",
    reason="ECL Client Tools required. Can't run on github runner",
)
@pytest.mark.parametrize(
    "job_name, expected_file, options, content, status",
    [
        (
            "Basic Job",
            "Basic_job.eclxml",
            {"-E": bool},
            "OUTPUT('HELLO WORLD!');",
            "success",
        ),
        ("Basic Job", "Basic_job.eclxml", None, "OUTPUT('HELLO WORLD!');", "success"),
    ],
)
def test_bash_compile_full(
    tmpdir, ws, job_name, options, expected_file, content, status
):
    working_directory = tmpdir
    output_file = ws.create_file_name(content, working_directory, job_name)
    output, error = ws.bash_compile(
        output_file,
        options,
    )
    assert os.path.exists(
        os.path.join(working_directory, ECL_OUTPUT_DIR, expected_file)
    )
    assert output["status"] == status


# Test if bash_run is working: Runs only in local
@pytest.mark.skipif(
    conftest.ENV != "LOCAL",
    reason="ECL Client Tools required. Can't run on github runner",
)
@pytest.mark.parametrize(
    "job_name, compile_options, content, show_command, run_options",
    [
        ("Basic Job", {"-E": bool}, "OUTPUT('HELLO WORLD!');", False, None),
        (
            "Basic Job",
            None,
            "OUTPUT('HELLO WORLD!');",
            True,
            {"--wait-connect": "5000"},
        ),
    ],
)
def test_bash_run_full(
    tmp_path, ws, job_name, compile_options, content, show_command, run_options
):
    working_directory = tmp_path
    output_file = ws.create_file_name(content, working_directory, job_name)
    output, error = ws.bash_compile(output_file, options=compile_options)
    output = ws.bash_run(output_file, options=run_options, show_command=show_command)
    assert output["wu_info"]["wuid"] is not None


# Test if WorkunitSubmit.create_workunit, WorkunitSubmit.compile_workunit and WorkunitSubmit.run_workunit can create, compile and run a workunit successfully
def test_run_workunit(ws, ecl_hello_query):
    wuid = ws.create_workunit(
        action=1,
        result_limit=100,
        query_text=ecl_hello_query,
        job_name="Test Run Workunit",
    )
    assert wuid is not None
    wustate = ws.compile_workunit(wuid=wuid)
    ws.wu_wait_compiled(wuid)
    assert wustate in [1, 3]
    state = ws.run_workunit(wuid=wuid)
    assert state != 4
    ws.wu_wait_complete(wuid=wuid)


# Test if an output directory for current workunit submit
def test_output_working_directory(tmp_path, hpcc, ecl_hello_query, clusters):
    ws = WorkunitSubmit(hpcc, clusters)
    working_directory = tmp_path
    output_folder = "output"
    ws.create_file_name(
        ecl_hello_query, working_directory, "Basic Job", output_folder="output"
    )
    assert os.path.exists(os.path.join(working_directory, output_folder))


# Test if RunConfig options are properly instantiated.
@pytest.mark.parametrize(
    "options, expected_options",
    [
        (
            None,
            {
                "--target": "thor",
                "--job-name": "Basic_Job",
                "--limit": 100,
                "-s": HPCC_HOST,
                "--port": f"{HPCC_PORT}",
                "-u": HPCC_USERNAME,
                "-pw": HPCC_PASSWORD,
            },
        ),
        (
            {"--target": "hthor", "--limit": 1000, "--job-name": "Basic Job 2"},
            {
                "--target": "hthor",
                "--job-name": "Basic Job 2",
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


# Test if get_least_active_cluster returns cluster
def test_get_least_active_cluster(ws):
    cluster = ws.get_least_active_cluster()
    assert cluster != ""
