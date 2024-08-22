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
    output, output_file = work_s.bash_compile(
        file_name,
    )
    print(output)
    print(output_file)

except Exception as e:
    print(e)
