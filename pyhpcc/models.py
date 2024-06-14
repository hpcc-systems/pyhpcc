import json
import logging
import os
import subprocess

import requests

import pyhpcc.config as conf
import pyhpcc.utils as utils
from pyhpcc.errors import HPCCException
from pyhpcc.roxie_binder import wrapper as roxie_wrapper
from pyhpcc.thor_binder import wrapper as thor_wrapper


class HPCC(object):
    """
    Base class for HPCC THOR API.

    Attributes:
    ----------
        auth:
            The authentication object
        timeout:
            The timeout for the requests
        response_type:
            The response type for the requests

    Methods:
    -------
        get_wu_info:
            Get the workunit information

        get_wu_result:
            Get the workunit result

        get_dfu_info:
            Get the DFU information

        wu_create_and_update:
            Create and update the workunit

        wu_submit:
            Submit the workunit

        wu_run:
            Run the workunit

        get_wu_query:
            Get the workunit query

        wu_query:
            Query the workunits using filters

        file_query:
            Query the files using filters

        get_file_info:
            Get the file information

        wu_wait_compiled:
            Wait for the workunit to be compiled

        wu_wait_complete:
            Wait for the workunit to be completed

        get_subfile_info:
            Get the subfile information

        check_file_exists:
            Check if the file exists

        tp_cluster_info:
            Get the cluster information

        activity:
            Get the activity information

        upload_file:
            Upload the file

        drop_zone_files:
            Get the dropzone files

        dfu_query:
            Query the DFU files using filters

        get_dfu_workunit_info:
            Get the DFU workunit information

        get_dfu_workunits:
            Get the DFU workunits

        spray_variable:
            Spray a file of variable length records

        spray_fixed:
            Spray a file of fixed format

        wu_update:
            Update the workunit

        get_graph:
            Get the graph information

        download_file:
            Download the file

        add_to_superfile_request:
            Add the file to the superfile

        file_list:
            Get the file list

    """

    def __init__(self, auth, timeout=1200, response_type="json"):
        self.auth = auth
        self.timeout = timeout
        self.response_type = response_type

    @property
    def get_wu_info(self):
        """Get information about a workunit"""
        return thor_wrapper(
            api=self,
            path="/WsWorkunits/WUInfo",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "TruncateEclTo64k",
                "IncludeExceptions",
                "IncludeGraphs",
                "IncludeSourceFiles",
                "IncludeResults",
                "IncludeResultsViewNames",
                "IncludeVariables",
                "IncludeTimers",
                "IncludeResourceURLs",
                "IncludeDebugValues",
                "IncludeApplicationValues",
                "IncludeWorkflows",
                "IncludeXmlSchemas",
                "SuppressResultSchemas",
                "rawxml_",
            ],
        )

    @property
    def get_wu_result(self):
        """Get the results of a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUResult",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "Sequence",
                "ResultName",
                "LogicalName",
                "Cluster",
                "false",
                "FilterBy",
                "Start",
                "Count",
            ],
        )

    @property
    def get_dfu_info(self):
        """Get information about a file"""
        return thor_wrapper(
            api=self,
            path="WsDfu/DFUInfo",
            payload_list=True,
            allowed_param=[
                "Name",
                "Cluster",
                "UpdateDescription",
                "FileName",
                "FileDesc",
            ],
        )

    @property
    def wu_create_and_update(self):
        """Create and update a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUCreateAndUpdate",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "State",
                "StateOrig",
                "Jobname",
                "JobnameOrig",
                "QueryText",
                "Action",
                "Description",
                "DescriptionOrig",
                "AddDrilldownFields",
                "ResultLimit",
                "Protected",
                "ProtectedOrig",
                "PriorityClass",
                "PriorityLevel",
                "Scope",
                "ScopeOrig",
                "ClusterSelection",
                "ClusterOrig",
                "XmlParams",
                "ThorSlaveIP",
                "QueryMainDefinition",
                "DebugValues",
                "ApplicationValues",
            ],
        )

    @property
    def wu_submit(self):
        """Submit a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUSubmit",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "Cluster",
                "Queue",
                "Snapshot",
                "MaxRunTime",
                "BlockTillFinishTimer",
                "SyntaxCheck",
                "NotifyCluster",
            ],
        )

    @property
    def wu_run(self):
        """Run a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WURun",
            payload_list=True,
            allowed_param=[
                "QuerySet",
                "Query",
                "Wuid",
                "CloneWorkunit",
                "Cluster",
                "Wait",
                "Input",
                "NoRootTag",
                "DebugValues",
                "Variables",
                "ApplicationValues",
                "ExceptionSeverity",
            ],
        )

    @property
    def get_wu_query(self):
        """Get the ECL query of a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUQuery",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "Type",
                "Cluster",
                "RoxieCluster",
                "Owner",
                "State",
                "StartDate",
                "EndDate",
                "ECL",
                "Jobname",
                "LogicalFile",
                "LogicalFileSearchType",
                "ApplicationValues",
                "After",
                "Before",
                "Count",
                "PageSize",
                "PageStartFrom",
                "PageEndAt",
                "LastNDays",
                "Sortby",
                "false",
                "CacheHint",
            ],
        )

    @property
    def wu_query(self):
        """Query workunits using filters"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUQuery",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "Type",
                "Cluster",
                "RoxieCluster",
                "Owner",
                "State",
                "StartDate",
                "EndDate",
                "ECL",
                "Jobname",
                "LogicalFile",
                "LogicalFileSearchType",
                "ApplicationValues",
                "After",
                "Before",
                "Count",
                "PageSize",
                "PageStartFrom",
                "PageEndAt",
                "LastNDays",
                "Sortby",
                "Descending",
                "CacheHint",
            ],
        )

    @property
    def file_query(self):
        """Query files using filters"""
        return thor_wrapper(
            api=self,
            path="WsDfu/DFUQuery",
            payload_list=True,
            allowed_param=[
                "LogicalName",
                "Description",
                "Owner",
                "RoxieCluster",
                "Owner",
                "NodeGroup",
                "FileSizeFrom",
                "FileSizeTo",
                "FileType",
                "StartDate",
                "EndDate",
                "ToTime",
                "PageStartFrom",
                "PageSize",
            ],
        )

    @property
    def get_file_info(self):
        """Get information about a file"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUResult",
            payload_list=True,
            allowed_param=["LogicalName", "Cluster", "Count"],
        )

    @property
    def wu_wait_compiled(self):
        """Wait for a workunit to compile"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUWaitCompiled",
            payload_list=True,
            allowed_param=["Wuid", "Wait", "ReturnOnWait"],
        )

    @property
    def wu_wait_complete(self):
        """Wait for a workunit to complete"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUWaitComplete",
            payload_list=True,
            allowed_param=["Wuid", "Wait", "ReturnOnWait"],
        )

    @property
    def get_subfile_info(self):
        """Get information about a subfile"""
        return thor_wrapper(
            api=self, path="WsDfu/DFUInfo", payload_list=True, allowed_param=["Name"]
        )

    @property
    def check_file_exists(self):
        """Check if a file exists"""
        return thor_wrapper(
            api=self,
            path="WsDfu/DFUQuery",
            payload_list=True,
            allowed_param=["LogicalName"],
        )

    @property
    def tp_cluster_info(self):
        """Get information about a cluster"""
        return thor_wrapper(
            api=self,
            path="WsTopology/TpClusterInfo",
            payload_list=True,
            allowed_param=["Name"],
        )

    @property
    def activity(self):
        """Get information about a workunit activity"""
        return thor_wrapper(
            api=self,
            path="WsSMC/Activity",
            payload_list=True,
            allowed_param=["Sortby", "Descending"],
        )

    @property
    def upload_file(self):
        """Upload a file to the HPCC"""
        return thor_wrapper(
            api=self,
            path="FileSpray/UploadFile",
            payload_list=True,
            allowed_param=["upload_", "rawxml_", "NetAddress", "Path", "OS"],
        )

    @property
    def drop_zone_files(self):
        """Get information about files in a dropzone"""
        return thor_wrapper(
            api=self,
            path="FileSpray/DropZoneFiles",
            payload_list=True,
            allowed_param=["id", "rawxml_"],
        )

    @property
    def dfu_query(self):
        """Query files using filters"""
        return thor_wrapper(
            api=self,
            path="WsDfu/DFUQuery",
            payload_list=True,
            allowed_param=[
                "Prefix",
                "NodeGroup",
                "ContentType",
                "LogicalName",
                "Description",
                "Owner",
                "StartDate",
                "EndDate",
                "FileType",
                "FileSizeFrom",
                "FileSizeTo",
                "FirstN",
                "PageSize",
                "PageStartFrom",
                "Sortby",
                "Descending",
                "OneLevelDirFileReturn",
                "CacheHint",
                "MaxNumberOfFiles",
                "IncludeSuperOwner",
            ],
        )

    @property
    def get_dfu_workunit_info(self):
        """Get information about a DFU workunit"""
        return thor_wrapper(
            api=self,
            path="FileSpray/GetDFUWorkunit",
            payload_list=True,
            allowed_param=["wuid"],
        )

    @property
    def get_dfu_workunits(self):
        """Get information about DFU workunits"""
        return thor_wrapper(
            api=self,
            path="FileSpray/GetDFUWorkunits",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "Owner",
                "Cluster",
                "StateReq",
                "Type",
                "Jobname",
                "PageSize",
                "CurrentPage",
                "PageStartFrom",
                "Sortby",
                "Descending",
                "CacheHint",
            ],
        )

    @property
    def spray_variable(self):
        """Spray a file to HPCC"""
        return thor_wrapper(
            api=self,
            path="FileSpray/SprayVariable",
            payload_list=True,
            allowed_param=[
                "sourceIP",
                "sourcePath",
                "srcxml",
                "sourceMaxRecordSize",
                "sourceFormat",
                "NoSourceCsvSeparator",
                "sourceCsvSeparate",
                "sourceCsvTerminate",
                "sourceCsvQuote",
                "sourceCsvEscape",
                "sourceRowTag",
                "destGroup",
                "destLogicalName",
                "overwrite",
                "replicate",
                "ReplicateOffset",
                "maxConnections",
                "throttle",
                "transferBufferSize",
                "prefix",
                "nosplit",
                "noRecover",
                "compress",
                "push",
                "pull",
                "encrypt",
                "decrypt",
                "failIfNoSourceFile",
                "recordStructurePresent",
                "quotedTerminator",
                "sourceRowPath",
                "isJSON",
            ],
        )

    @property
    def spray_fixed(self):
        """Spray a fixed file to HPCC"""
        return thor_wrapper(
            api=self,
            path="FileSpray/SprayFixed",
            payload_list=True,
            allowed_param=[
                "sourceIP",
                "sourcePath",
                "srcxml",
                "sourceFormat",
                "sourceRecordSize",
                "destGroup",
                "destLogicalName",
                "overwrite",
                "replicate",
                "ReplicateOffset",
                "maxConnections",
                "throttle",
                "transferBufferSize",
                "prefix",
                "nosplit",
                "norecover",
                "compress",
                "push",
                "pull",
                "encrypt",
                "decrypt",
                "wrap" "failIfNoSourceFile",
                "recordStructurePresent",
                "quotedTerminator",
            ],
        )

    @property
    def wu_update(self):
        """Update a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUUpdate",
            payload_list=True,
            allowed_param=[
                "Wuid",
                "State",
                "StateOrig",
                "Jobname",
                "JobnameOrig",
                "QueryText",
                "Action",
                "Description",
                "DescriptionOrig",
                "AddDrilldownFields",
                "ResultLimit",
                "Protected",
                "ProtectedOrig",
                "PriorityClass",
                "PriorityLevel",
                "Scope",
                "ScopeOrig",
                "ClusterSelection",
                "ClusterOrig",
                "XmlParams",
                "ThorSlaveIP",
                "QueryMainDefinition",
                "DebugValues",
                "ApplicationValues",
            ],
        )

    @property
    def get_graph(self):
        """Get a graph from a workunit"""
        return thor_wrapper(
            api=self,
            path="WsWorkunits/WUGetGraph",
            payload_list=True,
            allowed_param=["Wuid", "GraphName", "rawxml_"],
        )

    @property
    def download_file(self):
        """Download a file from the HPCC"""
        return thor_wrapper(
            api=self,
            path="FileSpray/DownloadFile",
            payload_list=True,
            allowed_param=["Name", "NetAddress", "Path", "OS"],
        )

    @property
    def add_to_superfile_request(self):
        """Add a file to a superfile"""
        return thor_wrapper(
            api=self,
            path="WsDfu/AddtoSuperfile",
            payload_list=True,
            allowed_param=["Superfile", "ExistingFile"],
        )

    @property
    def file_list(self):
        """List files in a directory"""
        return thor_wrapper(
            api=self,
            method="POST",
            path="FileSpray/FileList",
            payload_list=True,
            allowed_param=["Netaddr", "Path", "Mask", "OS", "rawxml_"],
        )


class Roxie(object):
    """
    Base class for HPCC Roxie API

    Attributes
    ----------
        auth:
            Authentication object
        timeout:
            Timeout for requests
        response_type:
            Type of response to return
        definition:
            Definition of the API
        search_service:
            Search service object
        roxie_port:
            Roxie port

    Methods
    -------
        __init__(auth, timeout, response_type, definition, search_service, roxie_port)
            Initialize the class

        roxie_call(self)
            Call the roxie API
    """

    def __init__(
        self,
        auth,
        search_service,
        roxie_port,
        timeout=1200,
        response_type="json",
        definition="submit",
    ):
        self.auth = auth
        self.timeout = timeout
        self.response_type = response_type
        self.definition = "WsEcl/" + definition + "/query"
        self.search_service = search_service
        self.roxie_port = roxie_port

    @property
    def roxie_call(self):
        """Call the roxie API

        Parameters
        ----------
            self:
                The object pointer

        Returns
        -------
            response:
                The response from the API

        """
        return roxie_wrapper(api=self)


class WorkunitSubmit(object):
    """
    Base class for HPCC workunit submit

    Attributes
    ----------
        hpcc:
            HPCC object
        cluster1:
            Cluster name
        cluster2:
            Cluster name

    Methods
    -------
        __init__
            Initialize the class

        write_file:
            Write a file to HPCC

        get_bash_command:
            Get the bash command to submit a workunit

        get_work_load:
            Get the workload on the clusters

        create_file_name:
            Create a filename for the workunit

        bash_compile:
            Compile the workunit

        bash_run:
            Run the workunit

        compile_workunit:
            Legacy function to compile the workunit

        create_workunit:
            Legacy function to create the workunit

        wu_wait_compiled:
            Legacy function to wait for the workunit to compile

        wu_wait_complete:
            Legacy function to wait for the workunit to complete

        run_workunit:
            Legacy function to run the workunit
    """

    def __init__(self, hpcc, cluster1="", cluster2=""):
        self.hpcc = hpcc
        self.cluster1 = cluster1
        self.cluster2 = cluster2
        self.stateid = conf.WORKUNIT_STATE_MAP

    def write_file(self, query_text, folder, job_name):
        """Write a .ecl file to disk

        Parameters
        ----------
            query_text:
                The ecl query to write
            folder:
                The folder to write the file to
            job_name:
                The name of the ecl file

        Returns
        -------
            file_name:
                The name of the ecl file written

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            words = job_name.split()
            job_name = "_".join(words)
            file_name = os.path.join(folder, job_name + ".ecl")
            f = open(file_name, "w")
            f.write(query_text)
            f.close
            return file_name
        except Exception as e:
            raise HPCCException("Could not write file: " + str(e))

    def get_bash_command(self, file_name, repository):
        """Get the bash command to compile the ecl file

        Parameters
        ----------
            file_name:
                The name of the ecl file
            repository:
                Git repository to use

        Returns
        -------
            bash_command:
                The bash command to compile the ecl file
            output_file:
                The name of the compiled ecl file - filename.eclxml

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            output_file = utils.create_compile_file_name(file_name)
            bash_command = utils.create_compile_bash_command(
                repository, output_file, file_name
            )
            return bash_command, output_file
        except Exception as e:
            raise HPCCException("Could not get bash command: " + str(e))

    def get_work_load(self):
        """Get the workload for the given two HPCC clusters

        Parameters
        ----------
            self:
                The object pointer

        Returns
        -------
            int, int:
                The number of jobs on each cluster

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            payload = {"SortBy": "Name", "Descending": 1}

            resp = self.hpcc.activity(**payload).json()
            len1 = 0
            len2 = 0
            if "Running" in list(resp["ActivityResponse"].keys()):
                workunits = resp["ActivityResponse"]["Running"]["ActiveWorkunit"]
                for workunit in workunits:
                    if workunit["TargetClusterName"] == self.cluster1:
                        len1 = len1 + 1
                    if workunit["TargetClusterName"] == self.cluster2:
                        len2 = len2 + 1

            return len1, len2

        except Exception as e:
            raise HPCCException("Could not get workload: " + str(e))

    def create_file_name(self, query_text, working_folder, job_name):
        """Create a filename for the ecl file

        Parameters
        ----------
            query_text:
                The ecl query
            working_folder:
                The folder to write the file to
            job_name:
                The name of the ecl file

        Returns
        -------
            file_name:
                The name of the ecl file

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            self.job_name = job_name
            return self.write_file(query_text, working_folder, job_name)
        except Exception as e:
            raise HPCCException("Could not create file name: " + str(e))

    def bash_compile(self, file_name, git_repository):
        """Compile the ecl file

        Parameters
        ----------
            file_name:
                The name of the ecl file
            git_repository:
                Git repository to use

        Returns
        -------
            output:
                The output from the bash command
            output_file:
                The name of the compiled ecl file - filename.eclxml

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            bash_command, output_file = self.get_bash_command(file_name, git_repository)
            process = subprocess.Popen(
                bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, error = process.communicate()
            return output, output_file
        except Exception as e:
            raise HPCCException("Could not compile: " + str(e))

    def bash_run(self, compiled_file, cluster):
        """Run the compiled ecl file

        Parameters
        ----------
            compiled_file:
                The name of the compiled ecl file
            cluster:
                The HPCC cluster to run the query on

        Returns
        -------
            output:
                The output from the bash command

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            # Select the cluster to run the query on
            if cluster == "":
                len1, len2 = self.get_work_load()
                if len2 > len1:
                    cluster = self.cluster1
                else:
                    cluster = self.cluster2

            self.job_name = self.job_name.replace(" ", "_")
            bash_command = utils.create_run_bash_command(
                compiled_file,
                cluster,
                self.hpcc.auth.ip,
                self.hpcc.auth.port,
                self.hpcc.auth.oauth[0],
                self.hpcc.auth.oauth[1],
                self.job_name,
            )
            process = subprocess.Popen(
                bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, error = process.communicate()

            return output, error
        except Exception as e:
            raise HPCCException("Could not run: " + str(e))

    def compile_workunit(self, wuid, cluster=""):
        """Legacy function to compile a workunit - use bash_compile instead

        Parameters
        ----------
            wuid:
                The Wuid of the workunit to compile
            cluster:
                The HPCC cluster to run the query on
        """
        if cluster == "":
            len1, len2 = self.get_work_load()
            if len2 > len1:
                cluster = self.cluster1
            else:
                cluster = self.cluster2
        self.hpcc.wu_submit(Wuid=wuid, Cluster=cluster)
        try:
            w3 = self.hpcc.wu_wait_compiled(Wuid=wuid)
        except requests.exceptions.Timeout:
            w3 = self.wu_wait_compiled(wuid=wuid)
            w3 = json.loads(w3.text)
            return w3["WUWaitResponse"]["StateID"]
        else:
            w3 = json.loads(w3.text)
            return w3["WUWaitResponse"]["StateID"]

    def create_workunit(
        self, action, result_limit, query_text, job_name, cluster_orig="", data=""
    ):
        """Legacy function to create a workunit - use bash_run instead

        Parameters
        ----------
            action:
                The action to perform
            result_limit:
                The number of results to return
            query_text:
                The ecl query
            job_name:
                The name of the ecl file
            cluster_orig:
                The HPCC cluster to run the query on
            data:
                The data to pass to the query
        """
        if cluster_orig == "":
            len1, len2 = self.get_work_load()

            if len2 > len1:
                cluster_orig = self.cluster1
            else:
                cluster_orig = self.cluster2
        if query_text is None:
            data = {"QueryText": data}
            kwargs = {"data": data}
        else:
            data = {"QueryText": query_text}
            kwargs = {"data": data}

        resp = self.hpcc.wu_create_and_update(
            Action=action,
            ResultLimit=result_limit,
            Jobname=job_name,
            ClusterOrig=cluster_orig,
            **kwargs,
        )

        if resp.status_code == 200:
            resp = json.loads(resp.text)
            if (
                "WUUpdateResponse" in resp
                and "Workunit" in resp["WUUpdateResponse"]
                and "Wuid" in resp["WUUpdateResponse"]["Workunit"]
            ):
                return resp["WUUpdateResponse"]["Workunit"]["Wuid"]

        else:
            raise ("workunit id not created")

    def wu_wait_compiled(self, wuid):
        """Legacy function to wait for a workunit to compile

        Parameters
        ----------
            Wuid:
                The Wuid of the workunit to compile
        """
        try:
            logging.info(
                "session timeout for wu_wait_compiled, starting new session for wu_wait_complete"
            )
            w4 = self.hpcc.wu_wait_compiled(Wuid=wuid)
        except requests.exceptions.Timeout:
            w4 = self.wu_wait_compiled(wuid=wuid)
            return w4
        else:
            return w4

    def wu_wait_complete(self, wuid):
        """Legacy function to wait for a workunit to complete

        Parameters
        ----------
            wuid:
                The Wuid of the workunit to compile
        """
        try:
            logging.info(
                "session timeout for WuRun, starting new session for wu_wait_complete"
            )
            w4 = self.hpcc.wu_wait_complete(Wuid=wuid)
        except requests.exceptions.Timeout:
            w4 = self.wu_wait_complete(wuid=wuid)
            return w4
        else:
            return w4

    def run_workunit(self, wuid, cluster=""):
        """Legacy function to run a workunit - use bash_run instead

        Parameters
        ----------
            wuid:
                The Wuid of the workunit to compile
            cluster:
                The HPCC cluster to run the query on
        """
        if cluster == "":
            len1, len2 = self.get_work_load()

            if len2 > len1:
                cluster = self.cluster1
            else:
                cluster = self.cluster2
        try:
            w4 = self.hpcc.wu_run(Wuid=wuid, Cluster=cluster, Variables=[])
        except requests.exceptions.Timeout:
            w4 = self.wu_wait_complete(wuid=wuid)
            w4 = w4.json()

            return w4["WUWaitResponse"]["StateID"]
        else:
            w4 = json.loads(w4.text)
            state = w4["WURunResponse"]["State"]
            return self.stateid[state]


class ReadFileInfo(object):
    """
    Class to read the file information from the HPCC cluster

    Attributes
    ----------
        hpcc:
            The hpcc object
        logical_file_name:
            The logical file name
        cluster:
            The cluster to read the file information from
        file_type:
            The file type
        file_size_limit:
            The file size limit. Defaults to 25MB
        if_exists:
            Boolean to determine if the file exists
        is_superfile:
            Boolean to determine if the file is a superfile
        actual_file_size:
            The actual file size
        record_count:
            The number of records in the file
        despray_ip:
            The IP address to despray the file to
        despray_path:
            The path to despray the file to
        despray_allow_overwrite:
            Boolean to determine if the file can be overwritten. Defaults to True
        should_despray:
            Boolean to determine if the file should be desprayed. Defaults to False
        check_status:
            Boolean to determine if the file status should be checked. Defaults to False
        csv_separator_for_read:
            The csv seperator for reading the file. Defaults to ','
        read_status:
            The read status. Defaults to 'Not Read'
        despray_from_cluster:
            The cluster to despray the file from
        csv_header_flag:
            Int to determine if the file has a csv header. Defaults to 0

    Methods
    -------
        check_if_file_exists_and_is_super_file:
            Checks if the file exists and is a superfile

        set_file_name:
            Sets the logical file name

        get_sub_file_information:
            Gets the subfile information

        check_file_in_dfu:
            Checks the file in the DFU queue

        get_data:
            Gets the data from the file
    """

    def __init__(
        self,
        hpcc,
        logical_file_name,
        cluster,
        file_type,
        file_size_limit=25,
        if_exists=-1,
        is_superfile=-1,
        actual_file_size=-1,
        record_count=-1,
        despray_ip="",
        despray_path="",
        despray_allow_overwrite="true",
        should_despray=False,
        check_status=False,
        csv_separator_for_read=",",
        read_status="Not read",
        despray_from_cluster="",
        csv_header_flag=0,
    ):
        """Constructor for the ReadFileInfo class"""

        self.hpcc = hpcc
        self.logical_file_name = logical_file_name
        self.cluster = cluster
        self.file_size_limit = file_size_limit
        self.file_type = file_type
        self.if_exists = if_exists
        self.if_superfile = is_superfile
        self.actual_file_size = actual_file_size
        self.record_count = record_count
        self.despray_ip = despray_ip
        self.despray_path = despray_path
        self.despray_allow_overwrite = despray_allow_overwrite
        self.should_despray = should_despray
        self.check_status = check_status
        self.csv_separator_for_read = csv_separator_for_read
        self.read_status = read_status
        self.despray_from_cluster = despray_from_cluster
        self.csv_header_flag = csv_header_flag

    def check_if_file_exists_and_is_super_file(self, cluster_from_user):
        """Function to check if the file exists and is a superfile

        Parameters
        ----------
            cluster_from_user:
                The cluster to check the file on
        """

        self.check_status = True
        file_search = self.hpcc.file_query(
            LogicalName=self.logical_file_name,
            LogicalFileSearchType="Logical Files and Superfiles",
        )
        self.if_exists = utils.get_file_status(file_search)
        if self.if_exists != 0 and self.if_exists != "0":
            arrFESF = utils.get_file_type(file_search)
            self.cluster = (
                arrFESF["NodeGroup"]
                if arrFESF["NodeGroup"] is not None
                else cluster_from_user
            )
            self.if_super_file = (
                arrFESF["isSuperfile"] if arrFESF["isSuperfile"] is not None else ""
            )
            self.actual_file_size = (
                int(arrFESF["Totalsize"].replace(",", ""))
                if arrFESF["Totalsize"] is not None
                else ""
            )
            self.file_type = (
                arrFESF["ContentType"]
                if arrFESF["ContentType"] is not None
                else self.file_type
            )
            if bool(arrFESF):
                if arrFESF["RecordCount"] != "":
                    self.record_count = (
                        0
                        if arrFESF["RecordCount"] is None
                        else int(arrFESF["RecordCount"].replace(",", ""))
                    )
                else:
                    self.record_count = -2
        else:
            self.file_type = ""
            self.if_super_file = ""
            self.actual_file_size = None
            self.record_count = None
            self.cluster = ""
            self.read_status = "File doesn't exist"

    def set_file_name(self, file_name):
        """Function to set the logical file name and check if the file exists and is a superfile

        Parameters
        ----------
            file_name:
                The logical file name
        """
        self.logical_file_name = file_name
        self.check_if_file_exists_and_is_super_file(self.cluster)

    def get_sub_file_information(self):
        """Function to get the subfile information

        Parameters
        ----------
            None

        Returns
        -------
            subFileInformation:
                The subfile information if the file is a superfile, else returns a message "Not a superfile"
        """
        if not self.check_status:
            self.check_if_file_exists_and_is_super_file(self.cluster)
        if self.if_superfile == 1:
            sub_file_info = self.hpcc.get_subfile_info(Name=self.logical_file_name)
            return utils.get_subfile_names(sub_file_info)
        else:
            return "Not a superfile"

    def check_file_in_dfu(self):
        """Function to check if the file exists in the DFU queue

        Parameters
        ----------
            None

        Returns
        -------
            dfuFileStatus:
                A boolean to determine if the file exists in the DFU queue
        """
        status_details = self.hpcc.check_file_exists(Name=self.logical_file_name)
        status = utils.check_file_existence(status_details)
        if status == 0:
            return False
        else:
            return True

    def get_data(self):
        """Function to get the data from the file

        Parameters
        ----------
            None

        Returns
        -------
            data:
                The data from the file
        """
        self.check_if_file_exists_and_is_super_file(self.cluster)
        if self.if_exists != 0 and self.if_exists != "0":
            file_size_in_mb = (self.actual_file_size / 1024) / 1024
            if (
                file_size_in_mb > self.file_size_limit
                or self.file_type == "xml"
                or self.should_despray
            ):
                if self.despray_ip != "" and self.despray_path != "":
                    query_string = (
                        "IMPORT STD; STD.file.despray(~'"
                        + self.logical_file_name
                        + "','"
                        + self.despray_ip
                        + "','"
                        + self.despray_path
                        + "',,,,"
                        + self.despray_allow_overwrite
                        + ");"
                    )
                    cluster_from = ""
                    if self.despray_from_cluster == "":
                        cluster_from = self.cluster
                    else:
                        cluster_from = self.despray_from_cluster
                    setattr(self.hpcc, "response_type", ".json")
                    self.read_status = utils.despray_file(
                        self.hpcc,
                        query_string,
                        cluster_from,
                        "Despraying : " + self.logical_file_name,
                    )
                else:
                    self.read_status = "Unable to despray with the given input values. Please provide values for despray IP and folder"
            else:
                if self.record_count == -2:
                    count_updated = 9223372036854775807
                else:
                    count_updated = self.record_count
                    flat_csv_resp = self.hpcc.get_file_info(
                        LogicalName=self.logical_file_name,
                        Cluster=self.cluster,
                        Count=count_updated,
                    )
                    if self.file_type == "flat":
                        self.read_status = "Read"
                        return utils.get_flat_data(flat_csv_resp)
                    else:
                        self.read_status = "Read"
                        return utils.get_csv_data(
                            flat_csv_resp,
                            self.csv_separator_for_read,
                            self.csv_header_flag,
                        )
        else:
            self.read_status = "File doesn't exist"
