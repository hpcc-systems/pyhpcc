.. _bash_compile:

Going deeper with WorkUnitSubmit ``bash_compile``
==================================================

Let's start with the ``bash_compile`` function definition.

.. py:function:: WorkUnitSubmit.bash_compile(self, file_name, [options: dict = None])

    Compile your workunit with the eclcc compiler
    
    :params: str: file_name
    :params: dict: options
    :return: parsed_output_json: **dict**, output_file: **str**
    :rtype: tuple

``bash_compile`` attaches some default compile options:

Let's see a simple example to understand

.. code-block:: python

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
            query_text=ecl_query, working_folder=working_folder, job_name=job_name
        )
        # Compile the ECL file
        output, output_file = work_s.bash_compile(file_name)
        print(output)
        print(output_file)

    except Exception as e:
        print(e)

The output will be similar if our file compiled successfully

.. code-block:: bash

    {'status': 'success', 'raw_output': '', 'bash_command': 'eclcc -platform thor -wu -E -o /Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.eclxml /Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl'}

Let's examine the ``bash_command`` in the output: 

.. code-block:: bash

    eclcc -platform thor -wu -E -o /Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.eclxml /Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl


We can notice a few things with the ecl command generated:
* By default, the ``-platform`` is ``thor``, ``-wu``, ``-E`` is set, and the output file is set with ``-o`` and is inferred and generated in the same directory of the input file.


Currently, ``bash_compile`` only supports XML output, so C++ options are not supported, and the flag ``-E`` is set for all compile.

Let's see how to configure ``options`` parameter in ``bash_compile``

* To set an ``option`` without value, use the key's value as a bool.
* To set an ``option`` with a value, use the key's value with the value you want to specify.

Let's see an example of setting the options

.. code-block:: python

    work_s.bash_compile(
        file_name,
        {
            "-qa": bool,
            "--logfile": "/path/to/ecl.log",
        },
    )

The ``bash_compile`` will produce the following eclcc command.

``eclcc -qa --logfile /path/to/ecl.log -o /Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.eclxml -E /Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl``


* ``-qa`` is set and ``--logfile`` is set with the value provided. Default flag ``-E`` is set as only xml output format is only supported.





