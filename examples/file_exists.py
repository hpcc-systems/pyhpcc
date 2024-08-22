from pyhpcc.models.auth import Auth
from pyhpcc.models.file import ReadFileInfo
from pyhpcc.models.hpcc import HPCC

# Example to check if a logical file exists

# Configurations
environment = (
    "university.us-hpccsystems-dev.azure.lnrsg.io"  # Eg: myuniversity.hpccsystems.io
)
port = "8010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "http"  # Specify HTTP or HTTPS
cluster = "thor"  # Specify the cluster name to be used
logical_file = "pyhpcc::testing::internet.csv"

try:
    auth_object = Auth(
        environment,
        port,
        user_name,
        password,
        protocol=protocol,
    )
    hpcc_object = HPCC(auth=auth_object)
    read_file = ReadFileInfo(
        hpcc=hpcc_object,
        logical_file_name=logical_file,
    )

    print(read_file.check_file_in_dfu())  # Prints `True` if file exists else `False`

except Exception as e:
    print(e)
