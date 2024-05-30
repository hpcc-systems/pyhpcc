import subprocess
import os
import json
import logging
import requests
import pandas as pd
from xml.etree import ElementTree as ET
from pyhpcc.thor_binder import wrapper as thor_wrapper
from pyhpcc.roxie_binder import wrapper as roxie_wrapper
from pyhpcc.errors import HPCCException
from pyhpcc.auth import auth
import pyhpcc.config as conf
import pyhpcc.utils as utils


class hpcc(object):
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
        get_wuinfo:
            Get the workunit information
        
        get_wuresult:
            Get the workunit result
        
        getdfuInfo:
            Get the DFU information
        
        wuCreateAndUpdate:
            Create and update the workunit
        
        wuSubmit:
            Submit the workunit
        
        wuRun:
            Run the workunit

        get_wuquery:
            Get the workunit query
        
        wuQuery:
            Query the workunits using filters
        
        fileQuery:
            Query the files using filters
        
        getFileInfo:
            Get the file information

        WUWaitCompiled:
            Wait for the workunit to be compiled

        WUWaitComplete:
            Wait for the workunit to be completed
        
        getSubFileInfo:
            Get the subfile information
        
        checkFileExists:
            Check if the file exists
        
        TpClusterInfo:
            Get the cluster information
        
        Activity:
            Get the activity information
        
        UploadFile:
            Upload the file

        DropZoneFiles:
            Get the dropzone files
        
        dfuQuery:
            Query the DFU files using filters
        
        getDfuWorkunitInfo:
            Get the DFU workunit information
        
        getDfuWorkunits:
            Get the DFU workunits
        
        sprayVariable:
            Spray a file of variable length records

        sprayFixed:
            Spray a file of fixed format 
        
        WUUpdate:
            Update the workunit

        getgraph:
            Get the graph information

        downloadfile:
            Download the file

        AddtoSuperfileRequest:
            Add the file to the superfile

        fileList:
            Get the file list

    """

    def __init__(self, auth, timeout=1200, response_type='json'):
        self.auth = auth
        self.timeout = timeout
        self.response_type = response_type

    @property
    def get_wuinfo(self):
        """Get information about a workunit
        """
        return thor_wrapper(api=self,
                            path='/WsWorkunits/WUInfo',
                            payload_list=True,
                            allowed_param=['Wuid',
                                           'TruncateEclTo64k',
                                           'IncludeExceptions',
                                           'IncludeGraphs',
                                           'IncludeSourceFiles',
                                           'IncludeResults',
                                           'IncludeResultsViewNames',
                                           'IncludeVariables',
                                           'IncludeTimers',
                                           'IncludeResourceURLs',
                                           'IncludeDebugValues',
                                           'IncludeApplicationValues',
                                           'IncludeWorkflows',
                                           'IncludeXmlSchemas',
                                           'SuppressResultSchemas',
                                           'rawxml_'])

    @property
    def get_wuresult(self):
        """Get the results of a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUResult', payload_list=True,
            allowed_param=['Wuid',
                           'Sequence',
                           'ResultName',
                           'LogicalName',
                           'Cluster',
                           'false',
                           'FilterBy',
                           'Start',
                           'Count'])

    @property
    def getdfuInfo(self):
        """Get information about a file
        """
        return thor_wrapper(
            api=self,
            path='WsDfu/DFUInfo', payload_list=True,
            allowed_param=["Name",
                           "Cluster",
                           "UpdateDescription",
                           "FileName",
                           "FileDesc"])

    @property
    def wuCreateAndUpdate(self):
        """Create and update a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUCreateAndUpdate', payload_list=True,
            allowed_param=['Wuid',
                           'State',
                           'StateOrig',
                           'Jobname',
                           'JobnameOrig',
                           'QueryText',
                           'Action',
                           'Description',
                           'DescriptionOrig',
                           'AddDrilldownFields',
                           'ResultLimit',
                           'Protected',
                           'ProtectedOrig',
                           'PriorityClass',
                           'PriorityLevel',
                           'Scope',
                           'ScopeOrig',
                           'ClusterSelection',
                           'ClusterOrig',
                           'XmlParams',
                           'ThorSlaveIP',
                           'QueryMainDefinition',
                           'DebugValues',
                           'ApplicationValues'])

    @property
    def wuSubmit(self):
        """Submit a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUSubmit', payload_list=True,
            allowed_param=['Wuid',
                           'Cluster',
                           'Queue',
                           'Snapshot',
                           'MaxRunTime',
                           'BlockTillFinishTimer',
                           'SyntaxCheck',
                           'NotifyCluster'])

    @property
    def wuRun(self):
        """Run a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WURun', payload_list=True,
            allowed_param=['QuerySet',
                           'Query',
                           'Wuid',
                           'CloneWorkunit',
                           'Cluster',
                           'Wait',
                           'Input',
                           'NoRootTag',
                           'DebugValues',
                           'Variables',
                           'ApplicationValues',
                           'ExceptionSeverity'])

    @property
    def get_wuquery(self):
        """Get the ECL query of a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUQuery', payload_list=True,
            allowed_param=['Wuid',
                           'Type',
                           'Cluster',
                           'RoxieCluster',
                           'Owner',
                           'State',
                           'StartDate',
                           'EndDate',
                           'ECL',
                           'Jobname',
                           'LogicalFile',
                           'LogicalFileSearchType',
                           'ApplicationValues',
                           'After',
                           'Before',
                           'Count',
                           'PageSize',
                           'PageStartFrom',
                           'PageEndAt',
                           'LastNDays',
                           'Sortby',
                           'false',
                           'CacheHint'])

    @property
    def wuQuery(self):
        """Query workunits using filters
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUQuery', payload_list=True,
            allowed_param=['Wuid',
                           'Type',
                           'Cluster',
                           'RoxieCluster',
                           'Owner',
                           'State',
                           'StartDate',
                           'EndDate',
                           'ECL',
                           'Jobname',
                           'LogicalFile',
                           'LogicalFileSearchType',
                           'ApplicationValues',
                           'After',
                           'Before',
                           'Count',
                           'PageSize',
                           'PageStartFrom',
                           'PageEndAt',
                           'LastNDays',
                           'Sortby',
                           'Descending',
                           'CacheHint'])

    @property
    def fileQuery(self):
        """Query files using filters
        """
        return thor_wrapper(
            api=self,
            path='WsDfu/DFUQuery', payload_list=True,
            allowed_param=['LogicalName',
                           'Description',
                           'Owner',
                           'RoxieCluster',
                           'Owner',
                           'NodeGroup',
                           'FileSizeFrom',
                           'FileSizeTo',
                           'FileType',
                           'StartDate',
                           'EndDate',
                           'ToTime',
                           'PageStartFrom',
                           'PageSize'])

    @property
    def getFileInfo(self):
        """Get information about a file
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUResult', payload_list=True,
            allowed_param=['LogicalName',
                           'Cluster',
                           'Count'])

    @property
    def WUWaitCompiled(self):
        """Wait for a workunit to compile
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUWaitCompiled', payload_list=True,
            allowed_param=['Wuid',
                           'Wait',
                           'ReturnOnWait'])

    @property
    def WUWaitComplete(self):
        """Wait for a workunit to complete
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUWaitComplete', payload_list=True,
            allowed_param=['Wuid',
                           'Wait',
                           'ReturnOnWait'])

    @property
    def getSubFileInfo(self):
        """Get information about a subfile
        """
        return thor_wrapper(
            api=self,
            path='WsDfu/DFUInfo', payload_list=True,
            allowed_param=['Name'])

    @property
    def checkFileExists(self):
        """Check if a file exists
        """
        return thor_wrapper(
            api=self,
            path='WsDfu/DFUQuery', payload_list=True,
            allowed_param=['LogicalName'])

    @property
    def TpClusterInfo(self):
        """Get information about a cluster
        """
        return thor_wrapper(
            api=self,
            path='WsTopology/TpClusterInfo', payload_list=True,
            allowed_param=['Name'])

    @property
    def Activity(self):
        """Get information about a workunit activity
        """
        return thor_wrapper(
            api=self,
            path='WsSMC/Activity', payload_list=True,
            allowed_param=['Sortby', 'Descending'])

    @property
    def UploadFile(self):
        """Upload a file to the HPCC
        """
        return thor_wrapper(api=self,
                            path='FileSpray/UploadFile',
                            payload_list=True,
                            allowed_param=['upload_',
                                           'rawxml_',
                                           'NetAddress',
                                           'Path',
                                           'OS']
                            )

    @property
    def DropZoneFiles(self):
        """Get information about files in a dropzone
        """
        return thor_wrapper(api=self,
                            path='FileSpray/DropZoneFiles',
                            payload_list=True,
                            allowed_param=['id',
                                           'rawxml_']
                            )

    @property
    def dfuQuery(self):
        """Query files using filters
        """
        return thor_wrapper(
            api=self,
            path='WsDfu/DFUQuery', payload_list=True,
            allowed_param=["Prefix",
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
                           "IncludeSuperOwner"])

    @property
    def getDfuWorkunitInfo(self):
        """Get information about a DFU workunit
        """
        return thor_wrapper(
            api=self,
            path='FileSpray/GetDFUWorkunit', payload_list=True,
            allowed_param=["wuid"])

    @property
    def getDfuWorkunits(self):
        """Get information about DFU workunits
        """
        return thor_wrapper(
            api=self,
            path='FileSpray/GetDFUWorkunits', payload_list=True,
            allowed_param=["Wuid",
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
                           "CacheHint", ])

    @property
    def sprayVariable(self):
        """Spray a file to HPCC
        """
        return thor_wrapper(
            api=self,
            path='FileSpray/SprayVariable', payload_list=True,
            allowed_param=["sourceIP",
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
                           "isJSON"]
        )

    @property
    def sprayFixed(self):
        """Spray a fixed file to HPCC
        """
        return thor_wrapper(
            api=self,
            path='FileSpray/SprayFixed', payload_list=True,
            allowed_param=["sourceIP",
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
                           "wrap"
                           "failIfNoSourceFile",
                           "recordStructurePresent",
                           "quotedTerminator"]
        )

    @property
    def WUUpdate(self):
        """Update a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUUpdate', payload_list=True,
            allowed_param=[
                'Wuid',
                'State',
                'StateOrig',
                'Jobname',
                'JobnameOrig',
                'QueryText',
                'Action',
                'Description',
                'DescriptionOrig',
                'AddDrilldownFields',
                'ResultLimit',
                'Protected',
                'ProtectedOrig',
                'PriorityClass',
                'PriorityLevel',
                'Scope',
                'ScopeOrig',
                'ClusterSelection',
                'ClusterOrig',
                'XmlParams',
                'ThorSlaveIP',
                'QueryMainDefinition',
                'DebugValues',
                'ApplicationValues',
            ]
        )

    @property
    def getgraph(self):
        """Get a graph from a workunit
        """
        return thor_wrapper(
            api=self,
            path='WsWorkunits/WUGetGraph', payload_list=True,
            allowed_param=['Wuid', 'GraphName', 'rawxml_'])

    @property
    def downloadfile(self):
        """Download a file from the HPCC
        """
        return thor_wrapper(
            api=self,
            path='FileSpray/DownloadFile', payload_list=True,
            allowed_param=['Name', 'NetAddress', 'Path', 'OS'])

    @property
    def AddtoSuperfileRequest(self):
        """Add a file to a superfile
        """
        return thor_wrapper(
            api=self,
            path='WsDfu/AddtoSuperfile', payload_list=True,
            allowed_param=['Superfile', 'ExistingFile'])

    @property
    def fileList(self):
        """List files in a directory
        """
        return thor_wrapper(
            api=self,
            method='POST',
            path='FileSpray/FileList', payload_list=True,
            allowed_param=['Netaddr', 'Path', 'Mask', 'OS', 'rawxml_'])


class roxie(object):
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
        searchservice:
            Search service object
        roxieport:
            Roxie port

    Methods
    -------
        __init__(auth, timeout, response_type, definition, searchservice, roxieport)
            Initialize the class

        roxie_call(self)
            Call the roxie API
    """

    def __init__(self,
                 auth,
                 searchservice,
                 roxie_port,
                 timeout=1200,
                 response_type='json',
                 definition='submit'):

        self.auth = auth
        self.timeout = timeout
        self.response_type = response_type
        self.definition = 'WsEcl/'+definition + '/query'
        self.searchservice = searchservice
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


class workunit_submit(object):
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
        
        get_bashcommand:
            Get the bash command to submit a workunit
        
        get_workload:
            Get the workload on the clusters

        create_filename:
            Create a filename for the workunit

        bash_compile:
            Compile the workunit
        
        bash_run:
            Run the workunit
        
        compileworkunit:
            Legacy function to compile the workunit
        
        createworkunit:
            Legacy function to create the workunit
        
        WUWaitCompiled:
            Legacy function to wait for the workunit to compile
        
        WUWaitComplete:
            Legacy function to wait for the workunit to complete
        
        runworkunit:
            Legacy function to run the workunit
    """
    def __init__(self, hpcc, cluster1='', cluster2=''):
        self.hpcc = hpcc
        self.cluster1 = cluster1
        self.cluster2 = cluster2
        self.stateid = conf.WORKUNIT_STATE_MAP

    def write_file(self, querytext, folder, jobname):
        """Write a .ecl file to disk
            
        Parameters
        ----------
            querytext:
                The ecl query to write
            folder:
                The folder to write the file to
            jobname:
                The name of the ecl file

        Returns
        -------
            filename:
                The name of the ecl file written
        
        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            words = jobname.split()
            jobname = '_'.join(words)
            filename = os.path.join(folder, jobname + '.ecl')
            f = open(filename, 'w')
            f.write(querytext)
            f.close
            return filename
        except Exception as e:
            raise HPCCException('Could not write file: ' + str(e))

    def get_bashcommand(self, filename, repository):
        """Get the bash command to compile the ecl file
        
        Parameters
        ----------
            filename:
                The name of the ecl file
            repository:
                Git repository to use

        Returns
        -------
            bashcommand:
                The bash command to compile the ecl file
            outputfile:
                The name of the compiled ecl file - filename.eclxml

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            outputfile = utils.create_compile_file_name(filename)
            bashcommand = utils.create_compile_bash_command(
                repository, outputfile, filename)
            return bashcommand, outputfile
        except Exception as e:
            raise HPCCException('Could not get bash command: ' + str(e))

    def get_workload(self):
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
            payload = {'SortBy': 'Name', 'Descending': 1}

            resp = self.hpcc.Activity(**payload).json()
            len1 = 0
            len2 = 0
            if 'Running' in list(resp['ActivityResponse'].keys()):
                workunits = resp['ActivityResponse']['Running']['ActiveWorkunit']
                for workunit in workunits:
                    if workunit['TargetClusterName'] == self.cluster1:
                        len1 = len1 + 1
                    if workunit['TargetClusterName'] == self.cluster2:
                        len2 = len2 + 1

            return len1, len2

        except Exception as e:
            raise HPCCException('Could not get workload: ' + str(e))

    def create_filename(self, QueryText, working_folder, Jobname):
        """Create a filename for the ecl file

        Parameters
        ----------
            QueryText:
                The ecl query
            working_folder:
                The folder to write the file to
            Jobname:
                The name of the ecl file

        Returns
        -------
            filename:
                The name of the ecl file            

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            self.Jobname = Jobname
            return self.write_file(QueryText, working_folder, Jobname)
        except Exception as e:
            raise HPCCException('Could not create filename: ' + str(e))

    def bash_compile(self,  filename, gitrepository):
        """Compile the ecl file

        Parameters
        ----------
            filename:
                The name of the ecl file
            gitrepository:
                Git repository to use

        Returns
        -------
            output:
                The output from the bash command
            outputfile:
                The name of the compiled ecl file - filename.eclxml

        Raises
        ------
            HPCCException:
                A generic exception
        """
        try:
            bashcommand, outputfile = self.get_bashcommand(
                filename, gitrepository)
            process = subprocess.Popen(
                bashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, error = process.communicate()
            return output, outputfile
        except Exception as e:
            raise HPCCException('Could not compile: ' + str(e))

    def bash_run(self, compiledfile, cluster):
        """Run the compiled ecl file

        Parameters
        ----------
            compiledfile:
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
            if cluster == '':
                len1, len2 = self.get_workload()
                if len2 > len1:
                    cluster = self.cluster1
                else:
                    cluster = self.cluster2

            self.Jobname = self.Jobname.replace(' ', '_')
            bashcommand = utils.create_run_bash_command(
                compiledfile, cluster, self.hpcc.auth.ip, self.hpcc.auth.port, self.hpcc.auth.oauth[0], self.hpcc.auth.oauth[1], self.Jobname)
            process = subprocess.Popen(
                bashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output, error = process.communicate()

            return output, error
        except Exception as e:
            raise HPCCException('Could not run: ' + str(e))

    def compileworkunit(self, Wuid, Cluster=''):
        """Legacy function to compile a workunit - use bash_compile instead

        Parameters
        ----------
            Wuid:
                The Wuid of the workunit to compile
            Cluster:
                The HPCC cluster to run the query on
        """
        if Cluster == '':
            len1, len2 = self.get_workload()
            if len2 > len1:
                Cluster = self.cluster1
            else:
                Cluster = self.cluster2
        self.hpcc.wuSubmit(Wuid=Wuid, Cluster=Cluster)
        try:
            w3 = self.hpcc.WUWaitCompiled(Wuid=Wuid)
        except requests.exceptions.Timeout:
            w3 = self.WUWaitCompiled(Wuid=Wuid)
            w3 = json.loads(w3.text)
            return w3['WUWaitResponse']['StateID']
        else:
            w3 = json.loads(w3.text)
            return w3['WUWaitResponse']['StateID']

    def createworkunit(self, Action, ResultLimit, QueryText, Jobname, ClusterOrig='', data=''):
        """Legacy function to create a workunit - use bash_run instead

        Parameters
        ----------
            Action:
                The action to perform
            ResultLimit:
                The number of results to return
            QueryText:
                The ecl query
            Jobname:
                The name of the ecl file
            ClusterOrig:
                The HPCC cluster to run the query on
            data:
                The data to pass to the query
        """
        if ClusterOrig == '':
            len1, len2 = self.get_workload()

            if len2 > len1:
                ClusterOrig = self.cluster1
            else:
                ClusterOrig = self.cluster2
        if QueryText is None:
            data = {'QueryText': data}
            kwargs = {'data': data}
        else:
            data = {'QueryText': QueryText}
            kwargs = {'data': data}

        resp = self.hpcc.wuCreateAndUpdate(Action=Action,
                                           ResultLimit=ResultLimit,
                                           Jobname=Jobname,
                                           ClusterOrig=ClusterOrig, **kwargs)

        if resp.status_code == 200:
            resp = json.loads(resp.text)
            if ('WUUpdateResponse' in resp
                and 'Workunit' in resp['WUUpdateResponse']
                    and 'Wuid' in resp['WUUpdateResponse']['Workunit']):
                return resp['WUUpdateResponse']['Workunit']['Wuid']

        else:
            raise ('workunit id not created')

    def WUWaitCompiled(self, Wuid):
        """Legacy function to wait for a workunit to compile

        Parameters
        ----------
            Wuid:
                The Wuid of the workunit to compile
        """
        try:
            logging.info(
                "session timeout for WUWaitCompiled, starting new session for WUWaitComplete")
            w4 = self.hpcc.WUWaitCompiled(Wuid=Wuid)
        except requests.exceptions.Timeout:
            w4 = self.WUWaitCompiled(Wuid=Wuid)
            return w4
        else:
            return w4

    def WUWaitComplete(self, Wuid):
        """Legacy function to wait for a workunit to complete

        Parameters
        ----------
            Wuid:
                The Wuid of the workunit to compile
        """
        try:
            logging.info(
                "session timeout for WuRun, starting new session for WUWaitComplete")
            w4 = self.hpcc.WUWaitComplete(Wuid=Wuid)
        except requests.exceptions.Timeout:
            w4 = self.WUWaitComplete(Wuid=Wuid)
            return w4
        else:
            return w4

    def runworkunit(self, Wuid, Cluster=''):
        """Legacy function to run a workunit - use bash_run instead

        Parameters
        ----------
            Wuid:
                The Wuid of the workunit to compile
            Cluster:
                The HPCC cluster to run the query on
        """
        if Cluster == '':
            len1, len2 = self.get_workload()

            if len2 > len1:
                Cluster = self.cluster1
            else:
                Cluster = self.cluster2
        try:
            w4 = self.hpcc.wuRun(Wuid=Wuid,
                                 Cluster=Cluster,
                                 Variables=[])
        except requests.exceptions.Timeout:
            w4 = self.WUWaitComplete(Wuid=Wuid)
            w4 = w4.json()

            return w4['WUWaitResponse']['StateID']
        else:
            w4 = json.loads(w4.text)
            state = w4['WURunResponse']['State']
            return self.stateid[state]


class readfileinfo(object):
    """
    Class to read the file information from the HPCC cluster
    
    Attributes
    ----------
        hpcc:
            The hpcc object
        logicalFileName:
            The logical file name
        cluster:
            The cluster to read the file information from
        fileType:
            The file type
        fileSizelimit:
            The file size limit. Defaults to 25MB
        ifExists:
            Boolean to determine if the file exists
        isSuperFile:
            Boolean to determine if the file is a superfile
        actualFileSize:
            The actual file size
        recordCount:
            The number of records in the file
        desprayIP:
            The IP address to despray the file to
        desprayPath:
            The path to despray the file to
        desprayallowoverwrite:
            Boolean to determine if the file can be overwritten. Defaults to True
        shouldDespray:
            Boolean to determine if the file should be desprayed. Defaults to False
        checkStatus:
            Boolean to determine if the file status should be checked. Defaults to False
        csvSeperatorforRead:
            The csv seperator for reading the file. Defaults to ','
        readStatus:
            The read status. Defaults to 'Not Read'
        desprayFromCluster:
            The cluster to despray the file from
        csvHeaderFlag:
            Int to determine if the file has a csv header. Defaults to 0
    
    Methods
    -------
        checkIfFileExistsAndIsSuperFile:
            Checks if the file exists and is a superfile
        
        setFilename:
            Sets the logical file name
        
        getSubFileInformation:
            Gets the subfile information

        checkfileinDFU:
            Checks the file in the DFU queue
    
        getData:
            Gets the data from the file
    """

    def __init__(self, hpcc, logicalFileName, cluster, fileType, fileSizelimit=25, ifExists=-1, isSuperFile=-1, actualFileSize=-1, recordCount=-1, desprayIP='', desprayPath='', desprayallowoverwrite='true', shouldDespray=False, checkStatus=False, csvSeperatorforRead=',', readStatus='Not read', desprayFromCluster='', csvHeaderFlag=0):
        """Constructor for the readfileinfo class"""

        self.hpcc = hpcc
        self.logicalFileName = logicalFileName
        self.cluster = cluster
        self.fileSizelimit = fileSizelimit
        self.fileType = fileType
        self.ifExists = ifExists
        self.isSuperFile = isSuperFile
        self.actualFileSize = actualFileSize
        self.recordCount = recordCount
        self.desprayIP = desprayIP
        self.desprayPath = desprayPath
        self.desprayallowoverwrite = desprayallowoverwrite
        self.shouldDespray = shouldDespray
        self.checkStatus = checkStatus
        self.csvSeperatorforRead = csvSeperatorforRead
        self.readStatus = readStatus
        self.desprayFromCluster = desprayFromCluster
        self.csvHeaderFlag = csvHeaderFlag

    def checkIfFileExistsAndIsSuperFile(self, clusterFromUser):
        """Function to check if the file exists and is a superfile

        Parameters
        ----------
            clusterFromUser:
                The cluster to check the file on
        """

        self.checkStatus = True
        fileSearch = self.hpcc.fileQuery(
            LogicalName=self.logicalFileName, LogicalFileSearchType='Logical Files and Superfiles')
        self.ifExists = utils.getfileStatus(fileSearch)
        if self.ifExists != 0 and self.ifExists != '0':
            arrFESF = utils.getfileType(fileSearch)
            self.cluster = arrFESF['NodeGroup'] if arrFESF['NodeGroup'] is not None else clusterFromUser
            self.ifSuperFile = arrFESF['isSuperfile'] if arrFESF['isSuperfile'] is not None else ''
            self.actualFileSize = int(arrFESF['Totalsize'].replace(
                ',', '')) if arrFESF['Totalsize'] is not None else ''
            self.fileType = arrFESF['ContentType'] if arrFESF['ContentType'] is not None else self.fileType
            if bool(arrFESF):
                if(arrFESF['RecordCount'] != ''):
                    self.recordCount = 0 if arrFESF['RecordCount'] is None else int(
                        arrFESF['RecordCount'].replace(',', ''))
                else:
                    self.recordCount = -2
        else:
            self.fileType = ''
            self.ifSuperFile = ''
            self.actualFileSize = None
            self.recordCount = None
            self.cluster = ''
            self.readStatus = "File doesn't exist"

    def setFilename(self, filename):
        """Function to set the logical file name and check if the file exists and is a superfile

        Parameters
        ----------
            filename:
                The logical file name
        """
        self.logicalFileName = filename
        self.checkIfFileExistsAndIsSuperFile(self.cluster)

    def getSubFileInformation(self):
        """Function to get the subfile information
        
        Parameters
        ----------
            None

        Returns
        -------
            subFileInformation:
                The subfile information if the file is a superfile, else returns a message "Not a superfile"
        """
        if(not self.checkStatus):
            self.checkIfFileExistsAndIsSuperFile(self.cluster)
        if(self.isSuperFile == 1):
            subFileInfo = self.hpcc.getSubFileInfo(Name=self.logicalFileName)
            return(utils.getSubfileNames(subFileInfo))
        else:
            return('Not a superfile')

    def checkfileinDFU(self):
        """Function to check if the file exists in the DFU queue

        Parameters
        ----------
            None

        Returns
        -------
            dfuFileStatus:
                A boolean to determine if the file exists in the DFU queue
        """
        statusDetails = self.hpcc.checkFileExists(Name=self.logicalFileName)
        status = utils.checkfileexistence(statusDetails)
        if status == 0:
            return False
        else:
            return True

    def getData(self):
        """Function to get the data from the file

        Parameters
        ----------
            None

        Returns
        -------
            data:
                The data from the file
        """
        self.checkIfFileExistsAndIsSuperFile(self.cluster)
        if self.ifExists != 0 and self.ifExists != '0':
            filesizeinMB = (self.actualFileSize/1024)/1024
            if(filesizeinMB > self.fileSizelimit or self.fileType == 'xml' or self.shouldDespray):
                if(self.desprayIP != '' and self.desprayPath != ''):
                    QueryString = "IMPORT STD; STD.file.despray(~\'"+self.logicalFileName + "\',\'" + \
                        self.desprayIP+"\',\'"+self.desprayPath + \
                        "\',,,,"+self.desprayallowoverwrite+");"
                    clusterfrom = ''
                    if(self.desprayFromCluster == ''):
                        clusterfrom = self.cluster
                    else:
                        clusterfrom = self.desprayFromCluster
                    setattr(self.hpcc, 'response_type', '.json')
                    self.readStatus = utils.desprayfile(
                        self.hpcc, QueryString, clusterfrom, 'Despraying : ' + self.logicalFileName)
                else:
                    self.readStatus = 'Unable to despray with the given input values. Please provide values for despray IP and folder'
            else:
                if(self.recordCount == -2):
                    countupdated = 9223372036854775807
                else:
                    countupdated = self.recordCount
                    flatcsvresp = self.hpcc.getFileInfo(
                        LogicalName=self.logicalFileName, Cluster=self.cluster, Count=countupdated)
                    if(self.fileType == 'flat'):
                        self.readStatus = 'Read'
                        return(utils.getflatdata(flatcsvresp))
                    else:
                        self.readStatus = 'Read'
                        return(utils.getcsvdata(flatcsvresp, self.csvSeperatorforRead, self.csvHeaderFlag))
        else:
            self.readStatus = "File doesn't exist"
