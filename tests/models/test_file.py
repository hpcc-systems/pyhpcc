import os
import time

import pytest
from pyhpcc.errors import HPCCException
from pyhpcc.models.file import ReadFileInfo


@pytest.fixture(
    autouse=True,
    scope="module",
    params=["employee_data.csv"],
)
def create_csv_test_data_in_server(
    request,
    hpcc,
    landing_zone_ip,
    landing_zone_path,
    csv_file,
    dfu_cluster,
):
    read_file_info = ReadFileInfo(hpcc, csv_file)
    is_present = read_file_info.check_file_in_dfu()
    if not is_present:
        landing_zone_file = request.param
        upload_file(hpcc, landing_zone_file, landing_zone_ip, landing_zone_path)
        spray_test_csv_file(
            hpcc,
            landing_zone_ip,
            landing_zone_path,
            landing_zone_file,
            csv_file,
            dfu_cluster,
        )
        # Giving time to the server, so the API's donot return FileNotFoundError
        time.sleep(2)


@pytest.fixture(
    autouse=True,
    scope="module",
    params=["employee_thor.csv"],
)
def create_flat_test_data_in_sever(
    request,
    hpcc,
    landing_zone_ip,
    landing_zone_path,
    logical_file,
    dfu_cluster,
):
    read_file_info = ReadFileInfo(hpcc, logical_file)
    is_present = read_file_info.check_file_in_dfu()
    if not is_present:
        landing_zone_file = request.param
        upload_file(hpcc, landing_zone_file, landing_zone_ip, landing_zone_path)
        spray_test_flat_file(
            hpcc,
            landing_zone_ip,
            landing_zone_path,
            landing_zone_file,
            logical_file,
            dfu_cluster,
        )


def upload_file(hpcc, file_name, landing_zone_ip, landing_zone_path):
    current_directory = os.getcwd()
    file_name = os.path.join(current_directory, "tests", "test_files", file_name)
    files = {
        "file": (
            file_name,
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

    assert (
        response["UploadFilesResponse"]["UploadFileResults"]["DFUActionResult"][0][
            "Result"
        ]
        == "Success"
    )


def spray_test_flat_file(
    hpcc, landing_zone_ip, landing_zone_path, landing_zone_file, flat_file, dfu_cluster
):
    payload = {
        "sourceIP": landing_zone_ip,
        "sourcePath": landing_zone_path + landing_zone_file,
        "sourceRecordSize": 458,
        "destGroup": dfu_cluster,
        "destLogicalName": flat_file,
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
    # wuid = response["SprayFixedResponse"]["wuid"]
    # payload = {"Wuid": wuid}
    # response = hpcc.wu_wait_complete(**payload).json()
    # assert response["WUWaitResponse"]["StateID"] in list(range(18))


def spray_test_csv_file(
    hpcc, landing_zone_ip, landing_zone_path, landing_zone_file, csv_file, dfu_cluster
):
    payload = {
        "sourceIP": landing_zone_ip,
        "sourcePath": landing_zone_path + landing_zone_file,
        "sourceCsvSeparate": "\\,",
        "sourceCsvTerminate": "\\n,\\r\\n",
        "destGroup": dfu_cluster,
        "destLogicalName": csv_file,
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
    assert dfu_id != ""


CSV_FILE_ROWS = 20000

FLAT_FILE_ROWS = 20000


def test_do_nothing():
    assert True


# Test if creation of ReadFileInfo raises error if no clusters are provided
def test_read_file_info_creation(hpcc, flat_file):
    try:
        read_file_info = ReadFileInfo(hpcc, flat_file)
        # assert read_file_info.cluster == "thor"
        assert read_file_info.infer_header
    except Exception as error:
        pytest.fail(
            f"Faced with exception while creating ReadFileInfo object {str(error)}"
        )


# Test if get_data_iter raises exception if file doesn't exist
def test_read_file_info_no_file_found(hpcc):
    read_file_info = ReadFileInfo(hpcc, "nofile")
    with pytest.raises(FileNotFoundError):
        next(read_file_info.get_data_iter(0, 1, 2))


# Test if get_data retrieves and handles headers
def test_get_data_iter_with_csv_headers(hpcc, csv_file):
    read_file_info = ReadFileInfo(hpcc, csv_file)
    data_attr, df = next(read_file_info.get_data_iter(0, -1, 10))
    assert data_attr["start"] == 1


# Test if get_data_iter retrieves all records if items_size is -1
def test_get_data_iter_no_of_records(hpcc, flat_file):
    read_file_info = ReadFileInfo(hpcc, flat_file)
    total_rows = 0
    for data_attr, df in read_file_info.get_data_iter(0, -1, 10000):
        total_rows += len(df)
    assert total_rows == FLAT_FILE_ROWS


# Test if get_data_iter fetches records as per start, count, batch_size for flat files
@pytest.mark.parametrize(
    "start, count, batch_size, result_length",
    [
        (0, 100, 21, 100),
        (1, 41, 19, 41),
        # (19000, 10000, 1000, 1000),
        (20001, 1000, 1000, 0),
        (20, 0, 10, 0),
    ],
)
def test_get_data_iter_flat_file(
    hpcc, flat_file, start, count, batch_size, result_length
):
    read_file_info = ReadFileInfo(hpcc, flat_file)
    total_rows = 0
    for data_attr, df in read_file_info.get_data_iter(start, count, batch_size):
        total_rows += len(df)
    assert total_rows == result_length


# Test if get_data_iter fetches records as per start, count, batch_size for csv files
@pytest.mark.parametrize(
    "start, count, batch_size, result_length, infer_header",
    [
        (0, 100, 21, 100, True),
        (1, 41, 19, 41, False),
        (1, 1050, 1020, 1050, False),
        (19000, 1000, 1000, 1000, True),
        (20001, 1000, 1000, 0, True),
        (20001, 1000, 1000, 0, False),
    ],
)
def test_get_data_iter_csv_file(
    hpcc, csv_file, start, count, batch_size, result_length, infer_header
):
    read_file_info = ReadFileInfo(hpcc, csv_file, infer_header=infer_header)
    total_rows = 0
    for data_attr, df in read_file_info.get_data_iter(start, count, batch_size):
        total_rows += len(df)
    assert total_rows == result_length


# Test if get_data fetches all records
def test_get_data_csv(hpcc, csv_file):
    read_file_info = ReadFileInfo(hpcc, csv_file)
    data_attr, df = read_file_info.get_data()
    assert len(df) == CSV_FILE_ROWS + 1


# Test if get_data throws error if file doesn't exist
def test_get_data_file_donot_exist(hpcc):
    read_file_info = ReadFileInfo(hpcc, "dummy::file::doesnt:exist")
    with pytest.raises(FileNotFoundError):
        data_attr, df = read_file_info.get_data()


# Test if get_sub_file_information_not_super_file return false for flat_file
def test_get_sub_file_information_not_super_file(hpcc, flat_file):
    read_file_info = ReadFileInfo(hpcc, flat_file)
    is_super, sub_files = read_file_info.get_sub_file_information()
    assert not is_super
    assert sub_files is None


# Test if get_sub_file_information_not_super_file return true and files are present for flat_file
def test_get_sub_file_information_super_file(hpcc, super_file):
    read_file_info = ReadFileInfo(hpcc, super_file)
    is_super, sub_files = read_file_info.get_sub_file_information()
    assert is_super
    assert sub_files is not None


# Test if check_file_in_dfu returns True if logicalfile is present
@pytest.mark.parametrize(
    "file",
    [("super_file"), ("flat_file"), ("csv_file")],
)
def test_check_file_in_dfu_pass(request, hpcc, file):
    file = request.getfixturevalue(file)
    read_file_info = ReadFileInfo(hpcc, file)
    assert read_file_info.check_file_in_dfu()


# Test if check_file_in_dfu returns False if logicalfile isn't present
@pytest.mark.parametrize(
    "file",
    [("pyhpccdi::employeed::dummies::datafds")],
)
def test_check_file_in_dfu_fail(hpcc, file):
    read_file_info = ReadFileInfo(hpcc, file)
    assert not read_file_info.check_file_in_dfu()
