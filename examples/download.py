from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC

# Example on downloading a file from dropzone

# Configurations
environment = (
    "play.hpccsystems.com"  # Eg: myuniversity.hpccsystems.io
)
port = "18010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "https"  # Specify HTTP or HTTPS
landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
landing_zone_ip = "."  # IP of dropzone
download_file_name = "california_housing_test.csv"  # file to be downloaded


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
    with open("california_housing_test.csv", "w") as download_file:
        download_file.write(response.text)
    print(download_file)    
except Exception as e:
    print(e)
