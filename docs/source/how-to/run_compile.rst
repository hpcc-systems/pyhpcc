.. _run_compile:

How to use WorkUnitSubmit to compile and run your ECL files
===============================================================

Let's see an example of compiling and running an inline ECL query.


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
        # Creates a work unit object. At least one cluster should be specified. ``remove_temp_files`` if set removes files created by workunit object
        work_s = ws(hpcc_object, (cluster,), remove_temp_files=True)
        # Create a file for the ECL query we want to execute
        file_name = work_s.create_file_name(
            query_text=ecl_query, working_folder=working_folder, job_name=job_name
        )
        # Compile the ECL file
        output, output_file = work_s.bash_compile(file_name)
        # check if the query is compiled without any errors
        if output["status"] == "success":
            # Run the ECL file that's compiled
            output = work_s.bash_run(output_file)
            # Check if work unit is created and wait on it for completion
            if (wuid := output["wu_info"]["wuid"]) is not None:
                resp = work_s.wu_wait_complete(wuid)
                print(resp.json())
    except Exception as e:
        print(e)



This is a lot of code to grasp. Let's break down and explain it step-by-step.


.. code-block:: python

    auth_object = Auth(
            environment,
            port,
            user_name,
            password,
            require_auth=True,
            protocol=protocol,
        )

* We are initializing the Auth object with the ``url``, ``port``, ``user_name`` and ``password``.
* We specify ``require_auth`` to True, hence requiring authentication.
* ``protocol`` parameter depends on if ``http`` or ``https`` is used.


.. code-block:: python

    hpcc_object = HPCC(auth=auth_object)

* An ``HPCC`` object is created which handles any API calls to HPCC Systems

.. code-block:: python

    work_s = ws(hpcc_object, (cluster,), remove_temp_files=True)

* ``WorkUnitSubmit`` object is created where we specify the clusters on which jobs are executed.



.. code-block:: python

    file_name = work_s.create_file_name(
            query_text=ecl_query, working_folder=working_folder, job_name=job_name
    )

* To compile an ecl query, we need to create a file to store our ECL query with ``job_name`` which specifies the file name, and ``working_folder``, which specifies the directory where the file should be created.


.. code-block:: python

    output, output_file = work_s.bash_compile(file_name)

* The ``bash_compile`` command compiles the code and returns compiler output and the output file created.



.. code-block:: python
    :linenos:

    if output["status"] == "success":
            # Run the ECL file that's compiled
            output = work_s.bash_run(output_file)
            # Check if workunit is created and wait on it for completion
            if (wuid := output["wu_info"]["wuid"]) is not None:
                resp = work_s.wu_wait_complete(wuid)
                print(resp.json())

* Line 1 checks if the ecl query compiled successfully
* Line 3 runs the ecl query with default run options. NOTE: bash_run options can also be configured with other parameters.
* Line 5 checks the return ``wuid`` and waits on it until completion.
* Line 7 prints the response returned by the wait API


