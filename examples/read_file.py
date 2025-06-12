from pyhpcc.models.auth import Auth
from pyhpcc.models.file import ReadFileInfo
from pyhpcc.models.hpcc import HPCC
from pyhpcc.models.workunit_submit import WorkunitSubmit as ws 

# Example illustrating how to read a logical file

# Configurations
environment = (
    "play.hpccsystems.com"  # Eg: myuniversity.hpccsystems.io
)
port = "18010"  # Eg: 8010
user_name = "user_name"  # HPCC username
password = "password"  # HPCC password
protocol = "https"  # Specify HTTP or HTTPS
cluster = "mythor"  # Specify the cluster name to be used
logical_file = "pyhpcc::testing::internet::thor"

try:
    auth_object = Auth(
        environment,
        port,
        user_name,
        password,
        protocol=protocol,
    )
    hpcc_object = HPCC(auth=auth_object)
    read_file = ReadFileInfo(hpcc=hpcc_object, logical_file_name=logical_file)
    
    # Retrieves all records with a `batch_size` of 2. To retrieve all records in one go, set the batch_size to a large number
    for data_attr, data in read_file.get_data_iter(0, -1, 5):
        print(data_attr)
        print(data)

except Exception as e:
    print(e)
