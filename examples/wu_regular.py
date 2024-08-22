from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC
from pyhpcc.models.workunit_submit import WorkunitSubmit as ws

# Example to show how to compile and run a inline ECL query using HPCC Systems REST API

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
    # Create workunit
    work_s = ws(hpcc_object, (cluster,), remove_temp_files=True)

    print("Creating workunit")
    wuid = work_s.create_workunit(
        action=1, result_limit=100, query_text=ecl_query, job_name=job_name
    )

    # Compile workunit
    wustate = work_s.compile_workunit(wuid=wuid)

    if wustate in [1, 3]:
        print("Running Workunit with ID " + str(wuid))
        state = work_s.run_workunit(wuid=wuid)
        print("Workunit with ID " + str(wuid) + ", State: " + str(state))
except Exception as e:
    print(e)
