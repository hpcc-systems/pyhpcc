from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC

# Example on spraying a csv file from dropzone

# Configurations
environment = (
    "play.hpccsystems.com"  # Eg: myuniversity.hpccsystems.io
)
port = "18010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "https"  # Specify HTTP or HTTPS
logical_file = "pyhpcc::testing::internet::csv"
landing_zone_ip = "."  # IP of dropzone
spray_file = "california_housing_test.csv"  # file to be sprayed from landing zone
landing_zone_path = "/var/lib/HPCCSystems/mydropzone/"  # Path in dropzone
dfu_cluster = "mythor"
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

except Exception as e:
    print(e)
