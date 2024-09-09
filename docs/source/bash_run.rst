.. _bash_run:

Going deeper with WorkUnitSubmit ``bash_run``
==================================================

Let's start with the ``bash_run`` function definition.


.. py:function:: WorkUnitSubmit.bash_run(self, compiled_file, [options: dict = None, show_command=False])

    Compile your workunit with the eclcc compiler
    
    :params: str: compiled_file
    :params: dict: options
    :return: parsed_response
    :rtype: dict


Let's run through a sample example.

.. code-block:: python
    :linenos:

    import os

    from pyhpcc.models.auth import Auth
    from pyhpcc.models.hpcc import HPCC
    from pyhpcc.models.workunit_submit import WorkunitSubmit as ws

    # Example to show how to compile and run an inline ECL query

    # Configurations
    environment = (
        "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
    )
    port = "8010"  # Eg: 8010
    user_name = "user_name"  # HPCC username
    password = "password"  # HPCC password
    protocol = "http"  # Specify HTTP or HTTPS
    cluster = "thor"  # Specify the cluster name to be used
    ecl_query = """OUTPUT('HELLO WORLD!');"""  # ECL Query to execute
    job_name = "Basic job submission"
    working_folder = os.getcwd()  # Folder to generate .ecl, .eclxml, .eclxml.xml

    try:
        auth_object = Auth(
            environment,
            port,
            user_name,
            password,
            require_auth=True,
            protocol=protocol,
        )
        hpcc_object = HPCC(auth=auth_object)
        work_s = ws(hpcc_object, (cluster,), remove_temp_files=True)
        # Create a file for the ECL query we want to execute
        file_name = work_s.create_file_name(
            query_text=ecl_query,
            working_folder=working_folder,
            job_name=job_name,
        )
        # Compile the ECL file
        output, output_file = work_s.bash_compile(file_name)
        # check if the query is compiled without any errors
        if output["status"] == "success":
            # Run the ECL file that's compiled
            output = work_s.bash_run(output_file, show_command=True)
            # Check if workunit is created and wait on it for completion
            if (wuid := output["wu_info"]["wuid"]) is not None:
                resp = work_s.wu_wait_complete(wuid)
                print(resp.json())

    except Exception as e:
        print(e)

Output of the code above

.. code-block:: bash

    {'WUWaitResponse': {'StateID': 3}}

Let's look at what `bash_run` is doing under the hood.

* Set the authorization parameters that are required to run the ecl query on the cluster.
* If no cluster is specified in the ``run config`` options, it finds the least active cluster from the least of clusters provided during ``WorkunitSubmit`` constructor initialization.
* If limit option (``--limit``) isn't provided, it sets the result to default limit ``100``

How to set ``RunConfig`` options and usage of ``show_command`` option:
------------------------------------

Previously we discussed about the defualt result limit (``100``).
What if we also need to set the ssl flag (``-ssl``)
    To set the above options, let's see how to do it.
.. code-block:: python
    :linenos:

    output = work_s.bash_run(output_file, options={"--limit": 200, "-ssl": bool}, show_command=True)
    print(output)

* Using the options parameter in bash_run we are able to set the ``limit`` and ``ssl`` flag.

Output of the above code:

.. code-block:: bash

    {
        "error": {"message": []},
        "raw_output": "<Raw output of ecl run>",
        "wu_info": {"wuid": "<wuid>", "state": "<state>"},
        "misc_info": {"message": []},
        "command": "ecl run /path/to/ecl-output/Basic_job_submission.eclxml --limit 200 -ssl --target thor --job-name Basic_job_submission -s university.us-hpccsystems-dev.azure.lnrsg.io --port 8010 -u username -pw ***** -v",
    }

* When we set the ``show_command`` in ``bash_run``, the output will include ``ecl run`` command used to execute. See the ``command`` field in the output above. 
* **NOTE**: To protect the privacy of the credentials used, the password is masked to `*****`