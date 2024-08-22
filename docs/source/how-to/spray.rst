.. _spray:

How to Spray files into DFU
==========================================

Spray a csv file
--------------------------
Lets see an example of how to spray a variable file (csv) from landing zone.

.. code-block:: python
    :linenos:

    from pyhpcc.models.auth import Auth
    from pyhpcc.models.hpcc import HPCC

    # Configurations
    environment = (
        "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
    )
    port = "8010"  # Eg: 8010
    user_name = "user_name"  # HPCC username
    password = "password"  # HPCC password
    protocol = "http"  # Specify HTTP or HTTPS
    logical_file = "pyhpcc::testing::internet::csv"
    landing_zone_ip = "localhost"  # IP of dropzone
    landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
    spray_file = "emp.csv"  # file to be sprayed from landing zone
    dfu_cluster = "data"
    try:
        auth_object = Auth(
            environment,
            port,
            user_name,
            password,
            protocol=protocol,
        )
        hpcc_object = HPCC(auth=auth_object)
        payload = {
            "sourceIP": landing_zone_ip,
            "sourcePath": landing_zone_path + spray_file,
            "sourceCsvSeparate": "\\,",
            "sourceCsvTerminate": "\\n,\\r\\n",
            "destGroup": dfu_cluster,
            "destLogicalName": logical_file,
            "overwrite": "on",
            "nosplit": "false",
            "compress": "false",
            "failIfNoSourceFile": "true",
            "sourceFormat": 1,  # TODO: Change according to file type
        }
        response = hpcc_object.spray_variable(**payload).json()
        print(response)
        wuid = print(response["SprayResponse"]["wuid"])

    except Exception as e:
        print(e)


Output:
~~~~~~~~

.. code-block:: bash

    {'SprayResponse': {'wuid': 'D20240716-234131'}}

* We used the ``HPCC`` object ``spray_variable`` method to spray our file.
* Create the payload to specify the ``landing_zone_ip``, ``landing_zone_path``, file to be sprayed and also the file type.
* Response with ``wuid`` is received on which we can check if the file is sprayed successfully.


Spray a thor file
-------------------------

Now let's see an example on spraying a fixed file

.. code-block:: python
    :linenos:
    :emphasize-lines: 26-37

    from pyhpcc.models.auth import Auth
    from pyhpcc.models.hpcc import HPCC

    # Configurations
    environment = (
        "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
    )
    port = "8010"  # Eg: 8010
    user_name = "user_name"  # HPCC username
    password = "password"  # HPCC password
    protocol = "http"  # Specify HTTP or HTTPS p
    logical_file = "pyhpcc::testing::internet::thor"
    landing_zone_ip = "localhost"  # IP of dropzone
    spray_file = "employee_data_thor"  # file to be sprayed from landing zone
    landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
    dfu_cluster = "data"
    try:
        auth_object = Auth(
            environment,
            port,
            user_name,
            password,
            protocol=protocol,
        )
        hpcc_object = HPCC(auth=auth_object)
        payload = {
            "sourceIP": landing_zone_ip,
            "sourcePath": landing_zone_path + spray_file,
            "sourceRecordSize": 151,  # TODO: Specify the record length of the THOR file
            "destGroup": dfu_cluster,
            "destLogicalName": logical_file,
            "overwrite": "on",
            "nosplit": "false",
            "compress": "false",
            "failIfNoSourceFile": "true",
        }
        response = hpcc_object.spray_fixed(**payload).json()
        print(response)

    except Exception as e:
        print(e)


Output:
~~~~~~~~

.. code-block:: bash
     
    {'SprayFixedResponse': {'wuid': 'D20240717-000527'}}


* Code to spray a fixed is similar to one as fixed, except the lines highlighted above where the changes are for  payload and method used.
* **Note**: A fixed file needs the record size parameter to be specified.
* Response with ``wuid`` is received on which we can check if the file is sprayed successfully. 