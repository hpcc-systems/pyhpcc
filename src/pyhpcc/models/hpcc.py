from pyhpcc.handlers.thor_handler import thor_handler


class HPCC(object):
    """
    Base class for HPCC THOR API.

    Attributes:
    ----------
        auth:
            The authentication object
        timeout:
            The timeout for the requests

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

    def __init__(self, auth, timeout=1200):
        self.auth = auth
        self.timeout = timeout
        self.response_type = "json"

    @property
    def get_wu_info(self):
        """Get information about a workunit"""
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
            api=self,
            path="WsWorkunits/WUResult",
            payload_list=True,
            allowed_param=["LogicalName", "Cluster", "Count"],
        )

    @property
    def wu_wait_compiled(self):
        """Wait for a workunit to compile"""
        return thor_handler(
            api=self,
            path="WsWorkunits/WUWaitCompiled",
            payload_list=True,
            allowed_param=["Wuid", "Wait", "ReturnOnWait"],
        )

    @property
    def wu_wait_complete(self):
        """Wait for a workunit to complete"""
        return thor_handler(
            api=self,
            path="WsWorkunits/WUWaitComplete",
            payload_list=True,
            allowed_param=["Wuid", "Wait", "ReturnOnWait"],
        )

    @property
    def get_subfile_info(self):
        """Get information about a subfile"""
        return thor_handler(
            api=self, path="WsDfu/DFUInfo", payload_list=True, allowed_param=["Name"]
        )

    @property
    def check_file_exists(self):
        """Check if a file exists"""
        return thor_handler(
            api=self,
            path="WsDfu/DFUQuery",
            payload_list=True,
            allowed_param=["LogicalName"],
        )

    @property
    def tp_cluster_info(self):
        """Get information about a cluster"""
        return thor_handler(
            api=self,
            path="WsTopology/TpClusterInfo",
            payload_list=True,
            allowed_param=["Name"],
        )

    @property
    def activity(self):
        """Get information about a workunit activity"""
        return thor_handler(
            api=self,
            path="WsSMC/Activity",
            payload_list=True,
            allowed_param=["Sortby", "Descending"],
        )

    @property
    def upload_file(self):
        """Upload a file to the HPCC"""
        return thor_handler(
            api=self,
            path="FileSpray/UploadFile",
            payload_list=True,
            allowed_param=["upload_", "rawxml_", "NetAddress", "Path", "OS"],
        )

    @property
    def drop_zone_files(self):
        """Get information about files in a dropzone"""
        return thor_handler(
            api=self,
            path="FileSpray/DropZoneFiles",
            payload_list=True,
            allowed_param=["id", "rawxml_"],
        )

    @property
    def dfu_query(self):
        """Query files using filters"""
        return thor_handler(
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
        return thor_handler(
            api=self,
            path="FileSpray/GetDFUWorkunit",
            payload_list=True,
            allowed_param=["wuid"],
        )

    @property
    def get_dfu_workunits(self):
        """Get information about DFU workunits"""
        return thor_handler(
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
        return thor_handler(
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
                "namePrefix",
            ],
        )

    @property
    def spray_fixed(self):
        """Spray a fixed file to HPCC"""
        return thor_handler(
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
        return thor_handler(
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
        return thor_handler(
            api=self,
            path="WsWorkunits/WUGetGraph",
            payload_list=True,
            allowed_param=["Wuid", "GraphName", "rawxml_"],
        )

    @property
    def download_file(self):
        """Download a file from the HPCC"""
        return thor_handler(
            api=self,
            path="FileSpray/DownloadFile",
            payload_list=True,
            allowed_param=["Name", "NetAddress", "Path", "OS"],
        )

    @property
    def add_to_superfile_request(self):
        """Add a file to a superfile"""
        return thor_handler(
            api=self,
            path="WsDfu/AddtoSuperfile",
            payload_list=True,
            allowed_param=["Superfile", "ExistingFile"],
        )

    @property
    def file_list(self):
        """List files in a directory"""
        return thor_handler(
            api=self,
            method="POST",
            path="FileSpray/FileList",
            payload_list=True,
            allowed_param=["Netaddr", "Path", "Mask", "OS", "rawxml_"],
        )
