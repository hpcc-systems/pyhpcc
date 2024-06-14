# Unit tests to test the authentication module
import os  # used by test_upload_file
import unittest
from datetime import datetime  # used by test_upload_file

import config

from pyhpcc.auth import Auth
from pyhpcc.errors import HPCCException
from pyhpcc.models import HPCC


class TestHPCCAPI(unittest.TestCase):
    HPCC_HOST = config.HPCC_HOST
    HPCC_PORT = config.HPCC_PORT
    HPCC_USERNAME = config.HPCC_USERNAME
    HPCC_PASSWORD = config.HPCC_PASSWORD
    DUMMY_USERNAME = config.DUMMY_USERNAME
    DUMMY_PASSWORD = config.DUMMY_PASSWORD
    DUMMY_HPCC_HOST = config.DUMMY_HPCC_HOST
    DUMMY_HPCC_PORT = config.DUMMY_HPCC_PORT

    AUTH_OBJ = Auth(HPCC_HOST, HPCC_PORT, HPCC_USERNAME, HPCC_PASSWORD, True, "https")
    HPCC_OBJ = HPCC(AUTH_OBJ)

    # Used by test_add_to_superfile_request, test_getSubFileInfoall
    # Generic superfile created for PyHPCC testing purposes on Boca Dataland
    SUPER_FILE_NAME = ""  # TODO: enter super file name

    # Used by test_get_dfu_info, test_get_file_info, test_check_file_exists, test_add_to_superfile_request, test_file_query
    # Generic logical file created for PyHPCC testing purposes on Boca Dataland
    LOGICAL_FILE_NAME = ""  # TODO: enter logical file name

    # Used by test_get_wu_info, test_get_wu_result
    # No particular reason why this wu was chosen. WU is on Boca Dataland. May have to be updated since it may get archived.
    STATIC_WUID = ""  # TODO: enter workunit id

    # Used by test_wu_submit, test_wu_wait_compiled, test_wu_run, test_wu_update
    # No particular reason why this wu was chosen. WU is on Boca Dataland. May have to be updated since it may get archived.
    STATIC_WUID2 = ""  # TODO: enter workunit id

    # Used by test_wu_wait_complete
    # Need to choose a workunit that is in the compile or run state, although any wuid will work for testing wu_wait_complete.
    # For state=unknown or state=paused, the wait will be infinite if the state is not updated for wu completion.
    STATIC_WUID3 = ""  # TODO: enter workunit id

    # Used by test_get_graph
    STATIC_WUID4 = ""  # TODO: enter workunit id

    # Used by test_get_wu_query
    STATIC_WUID5 = ""  # TODO: enter workunit id

    # Used by test_get_dfu_workunit_info
    # No particular reason why this wu was chosen. WU is on Boca Dataland. May have to be updated since it may get archived.
    STATIC_DFU_WUID = ""  # TODO: enter DFU workunit id

    # Used by test_upload_file
    # Points to bctlpedata12 landing zone. Used since this is a familiar landing zone.
    LANDING_ZONE_IP = ""  # TODO: Update with landing zone IP
    LANDING_ZONE_PATH = ""  # TODO: Update with landing zone path

    # Used by test_spray_fixed, test_spray_variable
    SPRAY_CLUSTER = ""  # TODO: Update with cluster name

    # Used by test_spray_fixed
    SPRAY_FIXED_SOURCE_FILE = ""  # TODO: Update with fixed spray source file path
    SPRAY_FIXED_DEST_FILE = ""  # TODO: Update with fixed spray destination file name

    # Used by test_spray_variable
    SPRAY_VARIABLE_SOURCE_FILE = ""  # TODO: Update with variable spray source file path
    SPRAY_VARIABLE_DEST_FILE = (
        ""  # TODO: Update with variable spray destination file name
    )

    # Used by test_download_file
    DOWNLOAD_FILE_NAME = ""  # TODO: Update with download file name

    def test_activity(self):
        payload = {"SortBy": "Name", "Descending": 1}
        response = self.HPCC_OBJ.activity(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        workunits_list = None
        if "Running" in list(response["ActivityResponse"].keys()):
            workunits_list = response["ActivityResponse"]["Running"]["ActiveWorkunit"]
        # workunits contains a list of dictionaries. Testing for an empty or populated list.
        self.assertGreaterEqual(len(workunits_list), 0)

    def test_file_list(self):
        payload = {
            "Netaddr": "",  # TODO: Update with landing zone IP
            "Path": "/data",
            "OS": 2,
        }
        response = self.HPCC_OBJ.file_list(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        files_list = None
        if "PhysicalFileStruct" in list(response["FileListResponse"]["files"].keys()):
            files_list = response["FileListResponse"]["files"]["PhysicalFileStruct"]
        # workunits contains a list of dictionaries. Testing for an empty or populated list.
        self.assertGreaterEqual(len(files_list), 0)

    def test_dfu_query(self):
        first_n_files = 10
        payload = {"FirstN": first_n_files}
        response = self.HPCC_OBJ.dfu_query(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        dfu_files_list = 0
        if "DFULogicalFile" in list(
            response["DFUQueryResponse"]["DFULogicalFiles"].keys()
        ):
            dfu_files_list = response["DFUQueryResponse"]["DFULogicalFiles"][
                "DFULogicalFile"
            ]
        self.assertEqual(len(dfu_files_list), first_n_files)

    def test_get_dfu_info(self):
        payload = {"Name": self.LOGICAL_FILE_NAME}
        response = self.HPCC_OBJ.get_dfu_info(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )
        self.assertEqual(
            self.LOGICAL_FILE_NAME, response["DFUInfoResponse"]["FileDetail"]["Name"]
        )

    def test_wu_query(self):
        page_size = 5
        payload = {"PageSize": page_size}
        response = self.HPCC_OBJ.wu_query(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        wu_list = 0
        if "ECLWorkunit" in list(response["WUQueryResponse"]["Workunits"].keys()):
            wu_list = response["WUQueryResponse"]["Workunits"]["ECLWorkunit"]
        self.assertEqual(len(wu_list), page_size)

    def test_get_wu_info(self):
        payload = {"Wuid": self.STATIC_WUID}
        response = self.HPCC_OBJ.get_wu_info(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )
        self.assertEqual(
            self.STATIC_WUID, response["WUInfoResponse"]["Workunit"]["Wuid"]
        )

    def test_get_dfu_workunits(self):
        page_size = 5
        payload = {"PageSize": page_size}
        response = self.HPCC_OBJ.get_dfu_workunits(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        dfu_wu_list = 0
        if "DFUWorkunit" in list(response["GetDFUWorkunitsResponse"]["results"].keys()):
            dfu_wu_list = response["GetDFUWorkunitsResponse"]["results"]["DFUWorkunit"]
        self.assertEqual(len(dfu_wu_list), page_size)

    def test_get_dfu_workunit_info(self):
        payload = {"wuid": self.STATIC_DFU_WUID}
        response = self.HPCC_OBJ.get_dfu_workunit_info(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )
        self.assertEqual(
            self.STATIC_DFU_WUID, response["GetDFUWorkunitResponse"]["result"]["ID"]
        )

    def test_get_wu_result(self):
        payload = {"Wuid": self.STATIC_WUID, "Sequence": 0}
        response = self.HPCC_OBJ.get_wu_result(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )
        self.assertEqual("Rules", response["WUResultResponse"]["Name"])

    def test_get_file_info(self):
        payload = {"LogicalName": self.LOGICAL_FILE_NAME}
        response = self.HPCC_OBJ.get_file_info(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        record_count = 100
        self.assertEqual(record_count, response["WUResultResponse"]["Count"])

    def test_tp_cluster_info(self):
        cluster_name = ""  # TODO: Update with cluster name
        payload = {"Name": cluster_name}
        response = self.HPCC_OBJ.tp_cluster_info(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )
        self.assertEqual(cluster_name, response["TpClusterInfoResponse"]["Name"])

    def test_get_subfile_info(self):
        payload = {"Name": self.SUPER_FILE_NAME}
        response = self.HPCC_OBJ.get_subfile_info(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertIn(
            "subfiles", list(response["DFUInfoResponse"]["FileDetail"].keys())
        )
        # superfiles can have no subfiles attached at times
        self.assertGreaterEqual(
            len(response["DFUInfoResponse"]["FileDetail"]["subfiles"]["Item"]), 0
        )

    def test_check_file_exists(self):
        payload = {"LogicalName": self.LOGICAL_FILE_NAME}
        response = self.HPCC_OBJ.check_file_exists(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertIn("DFUQueryResponse", list(response.keys()))
        # A file can exist which will result in a number > 0, or not exist which makes the number of files 0.
        self.assertGreaterEqual(response["DFUQueryResponse"]["NumFiles"], 0)

    def test_wu_create_and_update(self):
        cluster = ""  # TODO: Update with cluster name
        job_name = "PyHPCC Test Case"
        payload = {
            "Jobname": job_name,
            "QueryText": "Hello World",
            "Action": 1,
            "ResultLimit": 100,
            "ClusterOrig": cluster,
        }
        response = self.HPCC_OBJ.wu_create_and_update(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        if "Workunit" in list(response["WUUpdateResponse"]["Workunit"].keys()):
            self.assertEqual(
                job_name, response["WUUpdateResponse"]["Workunit"]["Jobname"]
            )

    # !!!IMPORTANT: Add to documentation: wu_submit compiles the workunit created in previous test case
    def test_wu_submit(self):
        # we need to retrieve the wuid created in the previous test case in this function to submit wu to cluster
        cluster = ""  # TODO: Update with cluster name
        payload = {"Wuid": self.STATIC_WUID2, "Cluster": cluster}
        response = self.HPCC_OBJ.wu_submit(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertIn("WUSubmitResponse", response)

    def test_wu_wait_compiled(self):
        payload = {"Wuid": self.STATIC_WUID2}
        response = self.HPCC_OBJ.wu_wait_compiled(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertIn("WUWaitResponse", response)

    # !!!IMPORTANT: Add to documentation: wuRun can only be used on compiled workunit ids
    def test_wu_run(self):
        # we need to retrieve the wuid created in the previous test case in this function to submit wu to cluster
        cluster = ""  # TODO: Update with cluster name
        payload = {"Wuid": self.STATIC_WUID2, "Cluster": cluster}
        response = self.HPCC_OBJ.wu_run(**payload).json()

        # !!!! may need to use the wait API call before asserting

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertIn(self.STATIC_WUID2, response["WURunResponse"]["Wuid"])
        self.assertIn("Hello World", response["WURunResponse"]["Results"])

    def test_wu_update(self):
        state = 0
        payload = {"Wuid": self.STATIC_WUID2, "State": state}
        response = self.HPCC_OBJ.WUUpdate(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertEqual(response["WUUpdateResponse"]["Workunit"]["StateID"], state)

    def test_wu_wait_complete(self):
        payload = {"Wuid": self.STATIC_WUID3}
        response = self.HPCC_OBJ.wu_wait_complete(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # states can be between 0 and 17(inclusive). See config.py file for wu state id mapping.
        self.assertIn(response["WUWaitResponse"]["StateID"], list(range(18)))

    def test_upload_file(self):
        current_directory = os.getcwd()
        file_name = os.path.join(
            current_directory, "tests", "test_files", "pyhpcc_spray_fixed.csv"
        )
        # ensure you update the extension of the file in the next line depending on the upload file type used in the previous line
        index = file_name.find(".csv")
        date_time_stamp = "{:%Y%m%d%H%M%S}".format(datetime.now())
        upload_file_name = file_name[:index] + date_time_stamp + file_name[index:]
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
            "NetAddress": self.LANDING_ZONE_IP,
            "OS": 2,
            "Path": self.LANDING_ZONE_PATH,
            "files": files,
        }
        response = self.HPCC_OBJ.upload_file(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        self.assertEqual(
            response["UploadFilesResponse"]["UploadFileResults"]["DFUActionResult"][0][
                "Result"
            ],
            "Success",
        )

    # OBSERVATION: a wu is created and runs successfully, but there are no contents. Check why the contents do not get listed under the content section.
    def test_spray_fixed(self):
        payload = {
            "sourceIP": self.LANDING_ZONE_IP,
            "sourcePath": self.SPRAY_FIXED_SOURCE_FILE,
            "sourceRecordSize": 2,
            "destGroup": self.SPRAY_CLUSTER,
            "destLogicalName": self.SPRAY_FIXED_DEST_FILE,
            "overwrite": "on",
            "nosplit": "false",
            "compress": "false",
            "failIfNoSourceFile": "true",
        }
        response = self.HPCC_OBJ.spray_fixed(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # A DFU workunit is created when spraying the file. Response returns this wuid.
        self.assertNotEqual(response["SprayFixedResponse"]["wuid"], "")

    def test_spray_variable(self):
        payload = {
            "sourceIP": self.LANDING_ZONE_IP,
            "sourcePath": self.SPRAY_VARIABLE_SOURCE_FILE,
            "sourceCsvSeparate": "\\,",
            "sourceCsvTerminate": "\\n,\\r\\n",
            "destGroup": self.SPRAY_CLUSTER,
            "destLogicalName": self.SPRAY_VARIABLE_DEST_FILE,
            "overwrite": "on",
            "nosplit": "false",
            "compress": "false",
            "failIfNoSourceFile": "true",
        }
        response = self.HPCC_OBJ.spray_variable(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # A DFU workunit is created when spraying the file. Response returns this wuid.
        self.assertNotEqual(response["SprayResponse"]["wuid"], "")

    # This test case will fail if the workunit id referred to is archived.
    def test_get_graph(self):
        payload = {"Wuid": self.STATIC_WUID4, "GraphName": "graph1"}
        response = self.HPCC_OBJ.get_graph(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # A DFU workunit is created when spraying the file. Response returns this wuid.
        self.assertEqual(
            response["WUGetGraphResponse"]["Graphs"]["ECLGraphEx"][0]["Label"],
            "RulesFile",
        )

    def test_get_wu_query(self):
        payload = {"Wuid": self.STATIC_WUID5}
        response = self.HPCC_OBJ.get_wu_query(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # A DFU workunit is created when spraying the file. Response returns this wuid.
        self.assertEqual(
            response["WUQueryResponse"]["Workunits"]["ECLWorkunit"][0]["Owner"],
            self.HPCC_USERNAME,
        )

    def test_file_query(self):
        payload = {"LogicalName": self.LOGICAL_FILE_NAME}
        response = self.HPCC_OBJ.file_query(**payload).json()

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # A DFU workunit is created when spraying the file. Response returns this wuid.
        self.assertEqual(
            response["DFUQueryResponse"]["DFULogicalFiles"]["DFULogicalFile"][0][
                "Name"
            ],
            self.LOGICAL_FILE_NAME,
        )

    def test_download_file(self):
        payload = {
            "Name": self.DOWNLOAD_FILE_NAME,
            "NetAddress": self.LANDING_ZONE_IP,
            "Path": self.LANDING_ZONE_PATH,
            "OS": 2,
        }
        response = self.HPCC_OBJ.download_file(**payload)

        if "Exceptions" in response:
            raise HPCCException(
                message=response["Exceptions"]["Exception"][0]["Message"]
            )

        # Downloading file would mean storing and parsing file contents on running server
        # so for simplicity, testing if response status code is 200
        self.assertEqual(response.status_code, 200)

    # !!! This test case will be uncommented for use once the remove subfile from a superfile feature API method is available
    # def test_add_to_superfile_request(self):
    #     payload = { 'Superfile': self.SUPER_FILE_NAME,
    #         'ExistingFile': 1,
    #         'names_i0': self.LOGICAL_FILE_NAME
    #       }
    #     response = self.HPCC_OBJ.add_to_superfile_request(**payload).json()

    #     if 'Exceptions' in response:
    #         raise HPCCException(message=response['Exceptions']['Exception'][0]['Message'])

    #     self.assertIn('AddtoSuperfileResponse', response)


if __name__ == "__main__":
    unittest.main()
