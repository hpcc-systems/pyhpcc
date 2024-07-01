import json
import logging
import os
import subprocess
from collections import Counter

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

        configure_run_config:
            Creates run config from given options
    """

    def __init__(
        self,
        hpcc: HPCC,
        clusters: tuple,
    ):
        if len(clusters) == 0:
            raise ValueError("Minimum one cluster should be specified")
        self.hpcc: HPCC = hpcc
        self.clusters: tuple = clusters
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
            if conf.OUTPUT_FILE_OPTION not in compile_config.options:
                output_file = utils.create_compile_file_name(file_name)
                compile_config.set_output_file(output_file)
            else:
                output_file = compile_config.get_option(conf.OUTPUT_FILE_OPTION)
            log.info(compile_config.options)
            bash_command = compile_config.create_compile_bash_command(file_name)
            log.info(bash_command)
            return bash_command, output_file
        except Exception as e:
            raise HPCCException("Could not get bash command: " + str(e))

    def get_least_active_cluster(self):
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
            if len(self.clusters) == 1:
                return self.clusters[0]
            payload = {"SortBy": "Name", "Descending": 1}
            return self.get_cluster_from_response(self.hpcc.activity(**payload).json())
        except Exception as e:
            raise HPCCException("Could not get workload: " + str(e))

    def get_cluster_from_response(self, resp):
        """Extract the cluster from the Activity API Response

        Parameters
        ----------
            self:
                The object pointer
            resp:
                Activity API response

        Returns
        -------
            str
                Cluster with least activity

        Raises
        ------
            HPCCException:
                A generic exception
        """
        cluster_activity = Counter(self.clusters)
        if "Running" in list(resp["ActivityResponse"].keys()):
            workunits = resp["ActivityResponse"]["Running"]["ActiveWorkunit"]
            for workunit in workunits:
                cluster = workunit["TargetClusterName"]
                if cluster in cluster_activity:
                    cluster_activity[cluster] -= 1
        return cluster_activity.most_common(1)[0][0]

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
            print(bash_command)
            process = subprocess.Popen(
                bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, error = process.communicate()
            parsed_output = utils.parse_bash_compile_output(output)
            return parsed_output, output_file
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
            run_config = self.configure_run_config(options)
            bash_command = run_config.create_run_bash_command(compiled_file)
            process = subprocess.Popen(
                bash_command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output, error = process.communicate()
            return utils.parse_bash_run_output(output)
        except RunConfigException:
            raise
        except Exception as e:
            raise HPCCException("Could not run: " + str(e))

    def configure_run_config(self, options: dict) -> RunConfig:
        """Creates run config from given options

        Parameters
        ----------
            options:
                dict of run config options

        Returns
        -------
            run_config:
                Returns RunConfig object configured with additional options
        """
        if options is None:
            options = conf.DEFUALT_RUN_OPTIONS
        run_config = RunConfig(options)
        if conf.CLUSTER_OPTION not in run_config.options:
            run_config.set_target(self.get_least_active_cluster())
        if conf.JOB_NAME_OPTION not in run_config.options:
            self.job_name = self.job_name.replace(" ", "_")
            run_config.set_job_name(self.job_name)
        if conf.LIMIT_OPTION not in run_config.options:
            run_config.set_limit(conf.DEFAULT_LIMIT)
        run_config.set_auth_params(self.hpcc.auth)
        return run_config

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
            cluster = self.get_least_active_cluster()

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
            cluster_orig = self.get_least_active_cluster()
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
            cluster = self.get_least_active_cluster()
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
