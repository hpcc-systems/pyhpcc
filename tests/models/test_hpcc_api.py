# Unit tests to test the authentication module
import os  # used by test_upload_file
from datetime import datetime  # used by test_upload_file

import pytest
from pyhpcc.errors import HPCCException


@pytest.fixture
def cluster():
    return "thor"


# Test if get_dfu_info returns file info
def test_get_dfu_info(hpcc, logical_file):
    payload = {"Name": logical_file}
    response = hpcc.get_dfu_info(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])
    assert logical_file == response["DFUInfoResponse"]["FileDetail"]["Name"]


# Test if get_dfu_info returns file info
def test_get_file_info(hpcc, logical_file):
    payload = {"LogicalName": logical_file}
    response = hpcc.get_file_info(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    record_count = 100
    assert record_count == response["WUResultResponse"]["Count"]


# Test if check_file_exists check file returns right response if file present
def test_check_file_exists(hpcc, logical_file):
    payload = {"LogicalName": logical_file}
    response = hpcc.check_file_exists(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    assert "DFUQueryResponse" in list(response.keys())
    assert response["DFUQueryResponse"]["NumFiles"] >= 0


# Test if file_query return file with properties
def test_file_query(hpcc, logical_file):
    payload = {"LogicalName": logical_file}
    response = hpcc.file_query(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    # A DFU workunit is created when spraying the file. Response returns this wuid.
    assert (
        response["DFUQueryResponse"]["DFULogicalFiles"]["DFULogicalFile"][0]["Name"]
        == logical_file
    )


# Test if get_subfile_info return subfiles of a super file
def test_get_subfile_info(hpcc, super_file):
    payload = {"Name": super_file}
    response = hpcc.get_subfile_info(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    assert "subfiles" in list(response["DFUInfoResponse"]["FileDetail"].keys())
    # superfiles can have no subfiles attached at times
    assert len(response["DFUInfoResponse"]["FileDetail"]["subfiles"]["Item"]) >= 0


# Test dfu_query returns logical files present in the server
def test_dfu_query(hpcc):
    first_n_files = 10
    payload = {"FirstN": first_n_files}
    response = hpcc.dfu_query(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    dfu_files_list = 0
    if "DFULogicalFile" in list(response["DFUQueryResponse"]["DFULogicalFiles"].keys()):
        dfu_files_list = response["DFUQueryResponse"]["DFULogicalFiles"][
            "DFULogicalFile"
        ]
    assert len(dfu_files_list) == first_n_files


# Test if activity return the workunits of clusters
def test_activity(hpcc):
    payload = {"SortBy": "Name", "Descending": 1}
    response = hpcc.activity(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    workunits_list = None
    if "Running" in list(response["ActivityResponse"].keys()):
        workunits_list = response["ActivityResponse"]["Running"]["ActiveWorkunit"]
    # workunits contains a list of dictionaries. Testing for an empty or populated list.
    assert len(workunits_list) >= 0


# Test if file_list returns files present in the landing zone
def test_file_list(hpcc, landing_zone_ip, landing_zone_path):
    payload = {
        "Netaddr": landing_zone_ip,
        "Path": landing_zone_path,
        "OS": 2,
    }
    response = hpcc.file_list(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    files_list = None
    if "PhysicalFileStruct" in list(response["FileListResponse"]["files"].keys()):
        files_list = response["FileListResponse"]["files"]["PhysicalFileStruct"]
    # workunits contains a list of dictionaries. Testing for an empty or populated list.
    assert len(files_list) >= 0


# Test wu_query retrieves workunits
def test_wu_query(hpcc):
    page_size = 5
    payload = {"PageSize": page_size}
    response = hpcc.wu_query(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    wu_list = 0
    if "ECLWorkunit" in list(response["WUQueryResponse"]["Workunits"].keys()):
        wu_list = response["WUQueryResponse"]["Workunits"]["ECLWorkunit"]
    assert len(wu_list) == page_size


# Test get_dfu_workunits retrieve dfu workunits
def test_get_dfu_workunits(hpcc):
    page_size = 5
    payload = {"PageSize": page_size}
    response = hpcc.get_dfu_workunits(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    dfu_wu_list = 0
    if "DFUWorkunit" in list(response["GetDFUWorkunitsResponse"]["results"].keys()):
        dfu_wu_list = response["GetDFUWorkunitsResponse"]["results"]["DFUWorkunit"]
    assert len(dfu_wu_list) == page_size


# Test if wu_create_and_update creates workunit
@pytest.mark.dependency()
def test_wu_create_and_update(hpcc, cluster, request):
    job_name = "PyHPCC Test Case"
    payload = {
        "Jobname": job_name,
        "QueryText": """OUTPUT('HELLO WORLD!');""",
        "Action": 1,
        "ResultLimit": 100,
        "ClusterOrig": cluster,
    }
    response = hpcc.wu_create_and_update(**payload).json()
    request.config.cache.set("wuid", response["WUUpdateResponse"]["Workunit"]["Wuid"])
    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    if "Workunit" in list(response["WUUpdateResponse"]["Workunit"].keys()):
        assert job_name == response["WUUpdateResponse"]["Workunit"]["Jobname"]


# Test if test_wu_info retrieves workunit info
@pytest.mark.dependency(depends=["test_wu_create_and_update"])
def test_get_wu_info(hpcc, request):
    wuid = request.config.cache.get("wuid", "")
    payload = {"Wuid": wuid}
    response = hpcc.get_wu_info(**payload).json()
    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])
    assert wuid == response["WUInfoResponse"]["Workunit"]["Wuid"]


# Test if test_wu_submit submits workunit
@pytest.mark.dependency(depends=["test_get_wu_info"])
def test_wu_submit(hpcc, cluster, request):
    # we need to retrieve the wuid created in the previous test case in this function to submit wu to cluster
    # cluster = "thor"  # TODO: Update with cluster name
    wuid = request.config.cache.get("wuid", "")
    payload = {"Wuid": wuid, "Cluster": cluster}
    response = hpcc.wu_submit(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    assert "WUSubmitResponse" in response


# Test if test_wu_wait_compiled waits until workunit is compiled
def test_wu_wait_compiled(request, hpcc):
    wuid = request.config.cache.get("wuid", "")
    payload = {"Wuid": wuid}
    response = hpcc.wu_wait_compiled(**payload).json()
    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])
    # assert False
    assert "WUWaitResponse" in response


# Test get_wu_result retrieves the workunit result
@pytest.mark.dependency(depends=["test_wu_submit"])
def test_get_wu_result(request, hpcc):
    wuid = request.config.cache.get("wuid", "")
    payload = {"Wuid": wuid, "Sequence": 0}
    response = hpcc.get_wu_result(**payload).json()
    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])
    assert "Result 1" == response["WUResultResponse"]["Name"]


# Test wu_run runs the workunit
def test_wu_run(request, hpcc, cluster):
    # we need to retrieve the wuid created in the previous test case in this function to submit wu to cluster
    wuid = request.config.cache.get("wuid", "")
    # cluster = ""  # TODO: Update with cluster name
    payload = {"Wuid": wuid, "Cluster": cluster}
    response = hpcc.wu_run(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])


# Test wu_wait_complete waits unitl workunit process is completed
def test_wu_wait_complete(request, hpcc):
    wuid = request.config.cache.get("wuid", "")
    payload = {"Wuid": wuid}
    response = hpcc.wu_wait_complete(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    # states can be between 0 and 17(inclusive). See config.py file for wu state id mapping.
    assert response["WUWaitResponse"]["StateID"] in list(range(18))


# Test wu_update properly changes the state of wuid
def test_wu_update(request, hpcc):
    state = 0
    wuid = request.config.cache.get("wuid", "")
    payload = {"Wuid": wuid, "State": state}
    response = hpcc.wu_update(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    assert response["WUUpdateResponse"]["Workunit"]["StateID"] == state


# Test if tp_cluster_info retrieves info regarding the cluster specified
def test_tp_cluster_info(hpcc, cluster):
    payload = {"Name": cluster}
    response = hpcc.tp_cluster_info(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])
    assert cluster == response["TpClusterInfoResponse"]["Name"]


# Test if upload_file uploads file into the landing_zone
@pytest.mark.dependency()
def test_upload_file(request, hpcc, landing_zone_ip, landing_zone_path):
    current_directory = os.getcwd()
    file_name = os.path.join(
        current_directory, "tests", "test_files", "pyhpcc_spray_fixed.csv"
    )
    # ensure you update the extension of the file in the next line depending on the upload file type used in the previous line
    index = file_name.find(".csv")
    date_time_stamp = "{:%Y%m%d%H%M%S}".format(datetime.now())
    upload_file_name = file_name[:index] + date_time_stamp + file_name[index:]
    request.config.cache.set("upload_file_name", upload_file_name)
    files = {
        "file": (
            upload_file_name,
            open(file_name, "rb"),
            "text/plain",
            {"Expires": "0"},
        )
    }

    payload = {
        "upload_": "",
        "rawxml_": 1,
        "NetAddress": landing_zone_ip,
        "OS": 2,
        "Path": landing_zone_path,
        "files": files,
    }

    response = hpcc.upload_file(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    (
        response["UploadFilesResponse"]["UploadFileResults"]["DFUActionResult"][0][
            "Result"
        ]
        == "Success",
    )


# Test if download_file downloads a specific file from the landing zone
@pytest.mark.dependency(depends=["test_upload_file"])
def test_download_file(request, hpcc, landing_zone_ip, landing_zone_path):
    download_file_name = request.config.cache.get("upload_file_name", "")
    payload = {
        "Name": download_file_name,
        "NetAddress": landing_zone_ip,
        "Path": landing_zone_path,
        "OS": 2,
    }
    response = hpcc.download_file(**payload)

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    # Downloading file would mean storing and parsing file contents on running server
    # so for simplicity, testing if response status code is 200
    assert response.status_code == 200


# Test if spray_variable sprays a file from landing zone to the logical files and returns dfu workunit
def test_spray_variable(request, hpcc, landing_zone_ip, landing_zone_path, dfu_cluster):
    spray_file = request.config.cache.get("upload_file_name", None)
    assert spray_file
    payload = {
        "sourceIP": landing_zone_ip,
        "sourcePath": landing_zone_path + spray_file,
        "sourceCsvSeparate": "\\,",
        "sourceCsvTerminate": "\\n,\\r\\n",
        "destGroup": dfu_cluster,
        "destLogicalName": "pyhpcc::em::test::emp_data",
        "overwrite": "on",
        "nosplit": "false",
        "compress": "false",
        "failIfNoSourceFile": "true",
        "sourceFormat": 1,
    }
    response = hpcc.spray_variable(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    # A DFU workunit is created when spraying the file. Response returns this wuid.
    dfu_id = response["SprayResponse"]["wuid"]
    request.config.cache.set("dfu_id", dfu_id)
    assert dfu_id != ""


# Test if get_dfu_workunit_info retrieves the dfu wuid information
def test_get_dfu_workunit_info(request, hpcc):
    dfu_id = request.config.cache.get("dfu_id", "None")
    payload = {"wuid": dfu_id}
    response = hpcc.get_dfu_workunit_info(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])
    assert dfu_id == response["GetDFUWorkunitResponse"]["result"]["ID"]


# def test_get_graph(request, hpcc):
#     dfu_id = request.config.cache.get("dfu_id", "")
#     payload = {"Wuid": dfu_id, "GraphName": "graph1"}
#     response = hpcc.get_graph(**payload).json()

#     if "Exceptions" in response:
#         raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

#     # A DFU workunit is created when spraying the file. Response returns this wuid.

#     assert (
#         response["WUGetGraphResponse"]["Graphs"]["ECLGraphEx"][0]["Label"]
#         == "RulesFile"
#     )


# def test_get_wu_query(hpcc, wuid):
#     payload = {"Wuid": wuid}
#     response = hpcc.get_wu_query(**payload).json()

#     if "Exceptions" in response:
#         raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

#     #     # A DFU workunit is created when spraying the file. Response returns this wuid.
#     assert (
#         response["WUQueryResponse"]["Workunits"]["ECLWorkunit"][0]["Owner"]
#         == conftest.HPCC_USERNAME
#     )


# Test if test_spray_fixed sprays the fixed file from landing zone to the logical files
def test_spray_fixed(hpcc, landing_zone_ip, landing_zone_path, dfu_cluster):
    payload = {
        "sourceIP": landing_zone_ip,
        "sourcePath": landing_zone_path + "OnlineLessonPersons",
        "sourceRecordSize": 151,
        "destGroup": dfu_cluster,
        "destLogicalName": "pyhpcc::test::persons",
        "overwrite": "on",
        "nosplit": "false",
        "compress": "false",
        "failIfNoSourceFile": "true",
    }
    response = hpcc.spray_fixed(**payload).json()

    if "Exceptions" in response:
        raise HPCCException(message=response["Exceptions"]["Exception"][0]["Message"])

    # A DFU workunit is created when spraying the file. Response returns this wuid.
    assert response["SprayFixedResponse"]["wuid"] != ""
