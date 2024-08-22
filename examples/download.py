from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC

# Example on downloading a file from dropzone

# Configurations
environment = (
    "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
)
port = "8010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "http"  # Specify HTTP or HTTPS
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
