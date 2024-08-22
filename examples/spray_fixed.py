from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC

# Example on spraying a fixed file from dropzone

# Configurations
environment = (
    "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
)
port = "8010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "http"  # Specify HTTP or HTTPS
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
