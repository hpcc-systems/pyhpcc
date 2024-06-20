import json
import logging
import os
import subprocess

import requests

import pyhpcc.config as conf
import pyhpcc.utils as utils
from pyhpcc.command_config import CompileConfig, RunConfig
from pyhpcc.errors import HPCCException, RunConfigException
from pyhpcc.models.hpcc import HPCC

log = logging.getLogger(__name__)


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

    def __init__(self, hpcc: HPCC, cluster1="", cluster2=""):
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

    def get_bash_command(self, file_name, compile_config: CompileConfig):
        """Get the bash command to compile the ecl file

        Parameters
        ----------
            file_name:
                The name of the ecl file
            config:
                CompileConfig object

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
            if "-o" not in compile_config.options:
                output_file = utils.create_compile_file_name(file_name)
                compile_config.set_output_file(output_file)
            bash_command = compile_config.create_compile_bash_command(file_name)
            log.info(bash_command)
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

    def bash_compile(self, file_name: str, options: dict = None):
        """Compile the ecl file

        Parameters
        ----------
            file_name:
                The name of the ecl file
            options:
                dictionary of eclcc compiler options

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
            if options is None:
                options = conf.DEFAULT_COMPILE_OPTIONS
            compile_config = CompileConfig(options)
            bash_command, output_file = self.get_bash_command(file_name, compile_config)
            process = subprocess.Popen(
                bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, error = process.communicate()
            return output, output_file
        except Exception as e:
            raise HPCCException("Could not compile: " + str(e))

    def bash_run(self, compiled_file, options: dict = None):
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
            if options is None:
                options = conf.DEFUALT_RUN_OPTIONS
            run_config = RunConfig(options)
            if conf.CLUSTER_PARAM not in run_config.options:
                len1, len2 = self.get_work_load()
                if len2 > len1:
                    cluster = self.cluster1
                else:
                    cluster = self.cluster2
                run_config.set_target(cluster)
            if conf.JOB_NAME_PARAM not in run_config.options:
                self.job_name = self.job_name.replace(" ", "_")
                run_config.set_job_name(self.job_name)
            if conf.LIMIT_PARAM not in run_config.options:
                run_config.set_limit(conf.DEFAULT_LIMIT)
            run_config.set_auth_params(self.hpcc.auth)
            bash_command = run_config.create_run_bash_command(compiled_file)
            process = subprocess.Popen(
                bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, error = process.communicate()

            return output, error
        except RunConfigException:
            raise
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
