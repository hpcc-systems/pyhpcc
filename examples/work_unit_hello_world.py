import os

from pyhpcc.models.auth import Auth
from pyhpcc.models.hpcc import HPCC
from pyhpcc.models.workunit_submit import WorkunitSubmit as ws

# Configurations
environment = "<Your environment url>"  # Eg: myuniversity.hpccsystems.io
port = "<Your port>"  # Eg: 8010
user_name = "<Your username>"
password = "<Your password>"
required_auth = True
protocol = "http"  # HTTP or HTTPS
cluster = "thor"  # Specify the cluster name to be used
cluster2 = "thor2"  # Another thor cluster
ecl_query = """OUTPUT('HELLO WORLD!');"""  # ECL Query to execute
job_name = "Basic job submission"
working_folder = os.getcwd()  # Folder to generate .ecl, .eclxml, .eclxml.xml

try:
    auth_object = Auth(
        environment,
        port,
        user_name,
        password,
        require_auth=required_auth,
        protocol=protocol,
    )
    hpcc_object = HPCC(auth=auth_object)
    work_s = ws(hpcc_object, cluster, cluster)
    file_name = work_s.create_file_name(
        query_text=ecl_query, working_folder=working_folder, Jobname=job_name
    )
    output, output_file = work_s.bash_compile(file_name=file_name, git_repository="")
    if str(output).find("error") == -1:
        output, error = work_s.bash_run(output_file, cluster=cluster)
        index = str(output).find("running")
        wuid = str(output)[: index - 1]
        _ = work_s.wu_wait_complete(wuid)
    else:
        print(str(output))
    print(f"{wuid} submitted successfully")

except Exception as e:
    print(e)
