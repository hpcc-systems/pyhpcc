import os

from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC

# Example on uploading a file to dropzone

# Configurations
environment = (
    "play.hpccsystems.com"  # Eg: myuniversity.hpccsystems.io
)
port = "18010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "https"  # Specify HTTP or HTTPS
cluster = "thor"  # Specify the cluster name to be used
landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
landing_zone_ip = "."  # IP of dropzone
file_name = "california_housing_test.csv"  # file to be uploaded


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
