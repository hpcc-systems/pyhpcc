import pyhpcc.utils as utils
import pytest


@pytest.mark.parametrize(
    "resp, expected_output",
    [
        (b"", {"status": "success", "raw_output": ""}),
        (
            b"Error: File 'Basic_job_submission.' does not exist\nNo input files could be opened\n",
            {
                "status": "error",
                "errors": ["Error: File 'Basic_job_submission.' does not exist"],
            },
        ),
        (
            b"/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl(1,8): error C2195: String constant is not terminated: \"'HELLO WORLD;\"\n/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl(1,21): error C3002: syntax error : expected ')'\n2 errors, 0 warning\n",
            {
                "status": "error",
                "errors": [
                    '/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl(1,8): error C2195: String constant is not terminated: "\'HELLO WORLD;"',
                    "/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/Basic_job_submission.ecl(1,21): error C3002: syntax error : expected ')'",
                ],
            },
        ),
        (
            b"Failed to compile Basic_job_submission.eclxml\nBasic_job_submission.eclxml.res.s(5,2): error C6003: unknown directive\nBasic_job_submission.eclxml.res.s(10,2): error C6003: unknown directive\nBasic_job_submission.eclxml.res.s(15,2): error C6003: unknown directive\nBasic_job_submission.eclxml(0,0): error C3000: Compile/Link failed for Basic_job_submission.eclxml (see //192.168.86.46/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/eclcc.log for details)\n\n---------- compiler output --------------\nBasic_job_submission.eclxml.res.s:5:2: error: unknown directive\n .size RESULT_XSD_1001_txt_start,339\n ^\nBasic_job_submission.eclxml.res.s:10:2: error: unknown directive\n .size BINWORKUNIT_1000_txt_start,1125\n ^\nBasic_job_submission.eclxml.res.s:15:2: error: unknown directive\n .size MANIFEST_1000_txt_start,182\n ^\n\n--------- end compiler output -----------\n4 errors, 0 warning\n",
            {
                "status": "error",
                "errors": [
                    "Failed to compile Basic_job_submission.eclxml",
                    "Basic_job_submission.eclxml.res.s(5,2): error C6003: unknown directive",
                    "Basic_job_submission.eclxml.res.s(10,2): error C6003: unknown directive",
                    "Basic_job_submission.eclxml.res.s(15,2): error C6003: unknown directive",
                    "Basic_job_submission.eclxml(0,0): error C3000: Compile/Link failed for Basic_job_submission.eclxml (see //192.168.86.46/Users/rohithsuryapodugu/Documents/GitHub/pyhpcc-internal/examples/eclcc.log for details)",
                ],
            },
        ),
    ],
)
def test_bash_compile(resp, expected_output):
    output = utils.parse_bash_compile_output(resp)
    expected_output["raw_output"] = resp.decode()
    assert output == expected_output


@pytest.mark.parametrize(
    "resp, expected_output",
    [
        (
            b"EXEC: Creating PIPE program process : '/opt/HPCCSystems/9.6.14/clienttools/bin/eclcc -E \"Basic_job_submission.ecl\" -fapplyInstantEclTransformations=1 -fapplyInstantEclTransformationsLimit=100' - hasinput=0, hasoutput=1 stderrbufsize=0 [] in (<cwd>)\nEXEC: Pipe: process 19789 complete 0\njsocket(9,2566) shutdown err = 57 : C!:52923 -> university.us-hpccsystems-dev.azure.lnrsg.io:8010 (5)\njsocket(9,2566) shutdown err = 57 : C!:52924 -> university.us-hpccsystems-dev.azure.lnrsg.io:8010 (5)\njsocket(9,2566) shutdown err = 57 : C!:52925 -> university.us-hpccsystems-dev.azure.lnrsg.io:8010 (5)\nUsing eclcc path /opt/HPCCSystems/9.6.14/clienttools/bin/eclcc\n\nDeploying ECL Archive Basic_job_submission.ecl\n\nDeployed\n   wuid: W20240701-115916\n   state: compiled\n\nRunning deployed workunit W20240701-115916\n<Result>\n<Dataset name='Result 1'>\n <Row><Result_1>HELLO WORLD</Result_1></Row>\n</Dataset>\n</Result>\n",
            {
                "wu_info": {"wuid": "W20240701-115916", "state": "compiled"},
                "misc_info": {
                    "message": [
                        "EXEC: Creating PIPE program process : '/opt/HPCCSystems/9.6.14/clienttools/bin/eclcc -E \"Basic_job_submission.ecl\" -fapplyInstantEclTransformations=1 -fapplyInstantEclTransformationsLimit=100' - hasinput=0, hasoutput=1 stderrbufsize=0 [] in (<cwd>)",
                        "EXEC: Pipe: process 19789 complete 0",
                        "<Result>",
                        "<Dataset name='Result 1'>",
                        "<Row><Result_1>HELLO WORLD</Result_1></Row>",
                        "</Dataset>",
                        "</Result>",
                    ]
                },
            },
        ),
        (
            b"EXEC: Creating PIPE program process : '/opt/HPCCSystems/9.6.14/clienttools/bin/eclcc -E \"Basic_job_submission.ecl\" -fapplyInstantEclTransformations=1 -fapplyInstantEclTransformationsLimit=100' - hasinput=0, hasoutput=1 stderrbufsize=0 [] in (<cwd>)\nEXEC: Pipe: process 21114 complete 0\njsocket(9,2566) shutdown err = 57 : C!:54803 -> university.us-hpccsystems-dev.azure.lnrsg.io:8010 (5)\njsocket(9,2566) shutdown err = 57 : C!:54805 -> university.us-hpccsystems-dev.azure.lnrsg.io:8010 (5)\n\n401: Unauthorized Access\nUsing eclcc path /opt/HPCCSystems/9.6.14/clienttools/bin/eclcc\n\nDeploying ECL Archive Basic_job_submission.ecl\n",
            {
                "error": {"message": ["401: Unauthorized Access"]},
                "wu_info": {"wuid": None, "state": None},
                "misc_info": {
                    "message": [
                        "EXEC: Creating PIPE program process : '/opt/HPCCSystems/9.6.14/clienttools/bin/eclcc -E \"Basic_job_submission.ecl\" -fapplyInstantEclTransformations=1 -fapplyInstantEclTransformationsLimit=100' - hasinput=0, hasoutput=1 stderrbufsize=0 [] in (<cwd>)",
                        "EXEC: Pipe: process 21114 complete 0",
                    ]
                },
            },
        ),
    ],
)
def test_bash_run(resp, expected_output):
    output = utils.parse_bash_run_output(resp)
    expected_output["raw_output"] = resp.decode()
    assert output == expected_output
