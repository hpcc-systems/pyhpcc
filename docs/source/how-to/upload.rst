.. _uploaddownload:

How to upload/download files from Dropzone
==========================================

Upload file to Dropzone
--------------------------
Lets see an example of uploading files to dropzone

.. code-block:: python
    :linenos:

    import os

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
    cluster = "thor"  # Specify the cluster name to be used
    landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
    landing_zone_ip = "localhost"  # IP of dropzone
    file_name = "emp.csv"  # file to be uploaded


    try:
        auth_object = Auth(
            environment,
            port,
            user_name,
            password,
            protocol=protocol,
        )
        hpcc_object = HPCC(auth=auth_object)
        current_directory = os.getcwd()
        file_name = os.path.join(current_directory, file_name)
        files = {
            "file": (
                file_name,
                open(file_name, "rb"),
                "text/plain",
                {"Expires": "0"},
            )
        }

        payload = {
            "upload_": "",
            "rawxml_": 1,
            "NetAddress": landing_zone_ip,
            "OS": 2,
            "Path": landing_zone_path,
            "files": files,
        }

        response = hpcc_object.upload_file(**payload).json()
        print(response)

    except Exception as e:
        print(e)


``HPCC`` provides an easy way to uploading files to the server, Lets run over the step-by-step

* We are opening the file that we want to upload in the lines ``29-38``
* To workwith the API, we have provide details for the API to specify ``landing_zone_ip`` and  ``landing_zone_path`` of the dropzone.   
* We used ``HPCC`` object upload_file to upload the file.

Below is the response if the file successfully got uploaded.

.. code-block:: bash

    {'UploadFilesResponse': {'UploadFileResults': {'DFUActionResult': [{'ID': '/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/emp.csv', 'Action': 'Upload File', 'Result': 'Success'}]}}}



Download file from Dropzone
-----------------------------

- Lets try to download the file we uploaded in the previous section

.. code-block:: python
    :linenos:

    from pyhpcc.models.auth import Auth
    from pyhpcc.models.hpcc import HPCC

    # Configurations
    environment = (
        "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
    )
    port = "8010"  # Eg: 8010
    user_name = "dummyusername"  # HPCC username
    password = "dummypassword"  # HPCC password
    protocol = "http"  # Specify HTTP or HTTPS p
    landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
    landing_zone_ip = "localhost"  # IP of dropzone
    download_file_name = "emp.csv"  # file to be downloaded


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
            "Name": download_file_name,
            "NetAddress": landing_zone_ip,
            "Path": landing_zone_path,
            "OS": 2,
        }
        response = hpcc_object.download_file(**payload)
        with open("emp-download.csv", "w") as download_file:
            download_file.write(response.text)
    except Exception as e:
        print(e)


Let's run through the code again

* In the ``payload`` we specify the ``download_file_name`` to be downloaded, ``landing_zone_ip``, ``landing_zone_path``
* We make the API call using ``HPCC`` object which retrieves the file content.
* We create a file ``emp-download.csv`` to write the downloaded contents to it.