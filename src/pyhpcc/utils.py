import re
import sys

import pandas as pd
import six

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
from pyhpcc.config import (
    COMPILE_ERROR_MIDDLE_PATTERN,
    COMPILE_ERROR_PATTERN,
    FAILED_STATUS,
    RUN_ERROR_MSG_PATTERN,
    RUN_UNWANTED_PATTERNS,
    STATE,
    STATE_PATTERN,
    WUID,
    WUID_PATTERN,
)
from pyhpcc.errors import HPCCException

"""
This module contains utility functions for the pyhpcc package.
"""
DFU_LOGICAL_FILES = "DFULogicalFiles"
DFU_QUERY_RESPONSE = "DFUQueryResponse"
DFU_LOGICAL_FILE = "DFULogicalFile"


def convert_arg_to_utf8_str(arg):
    """
    Convert an argument to a UTF-8 encoded string.
    If the argument is a unicode string, encode it to UTF-8
    If the argument is not of type bytes, convert it to a string using str() and then encode it to UTF-8.
    If the argument is of type bytes, return it as is.

    Parameters
    ----------
    arg : str or bytes
        The argument to convert.

    Returns
    -------
    str or bytes
        The UTF-8 encoded string representation of the argument.

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        if isinstance(arg, six.string_types):
            return arg.encode("utf-8")

        elif not isinstance(arg, six.binary_type):
            return str(arg).encode("utf-8")

        return arg
    except HPCCException as e:
        raise e


def create_compile_file_name(file_name):
    """
    Create a compiled file name from a filename.

    Parameters
    ----------
    file_name : str
        The ecl filename to create a compiled file name from.

    Returns
    -------
    str
        The compiled file name.

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        return file_name.split(".")[0] + ".eclxml"
    except HPCCException as e:
        raise e


# TODO: Revise method

# def get_graph_skew(response):
#     """
#     Get the graph skew from the response of a WUInfo call.

#     Parameters
#     ----------
#     response :
#         str

#     Returns
#     -------
#     dict :
#         A dictionary containing the graph skew information.

#     Raises
#     ------
#     HPCCException
#         A generic exception.
#     """
#     try:
#         resp_json = response.json()
#         graphs = []
#         xml = resp_json["WUGetGraphResponse"]["Graphs"]["ECLGraphEx"][0]["Graph"]
#         root = ET.fromstringlist(xml)

#         # Loop through the graph nodes and get the skew information
#         for node in root.findall("./node/att/graph/node"):
#             graph = {"subgraphid": node.get("id")}
#             for child in node:
#                 if child.get("name") == "SkewMaxLocalExecute":
#                     graph["skewmax"] = child.get("value")
#                 if child.get("name") == "TimeAvgLocalExecute":
#                     graph["avgtime"] = child.get("value")
#                 if child.get("ecl") == "TimeAvgLocalExecute":
#                     graph["ecl"] = child.get("value")
#             graphs.append(graph)

#         return graphs

#     except HPCCException as e:
#         raise e


def get_file_status(response):
    """
    Parses the xml response to get NumFiles information

    Parameters
    ----------
    response :
        Response Object

    Returns
    -------
    str
        Number of files

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        NUM_FILES = "NumFiles"
        DFU_QUERY_RESPONSE = "DFUQueryResponse"
        response = response.json()
        response = response[DFU_QUERY_RESPONSE]
        if NUM_FILES in response:
            return response[NUM_FILES]
        else:
            return 0
    except HPCCException as e:
        raise e


def get_file_type(response):
    """
    Parses the JSON response to get FileType information

    Parameters
    ----------
    response : Response
        The Response object

    Returns
    -------
    dict
        A dictionary containing the FileType information

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        response = response.json()
        data_dict = {}
        NODE_GROUP = "NodeGroup"
        IS_SUPER_FILE = "isSuperfile"
        TOTAL_SIZE = "Totalsize"
        RECORD_COUNT = "RecordCount"
        CONTENT_TYPE = "ContentType"

        ATTRIBUTES = [NODE_GROUP, IS_SUPER_FILE, TOTAL_SIZE, RECORD_COUNT, CONTENT_TYPE]
        # Loop through the JSON and get the FileType information
        if DFU_QUERY_RESPONSE in response:
            response = response[DFU_QUERY_RESPONSE]
            if DFU_LOGICAL_FILES in response:
                response = response[DFU_LOGICAL_FILES]
                if DFU_LOGICAL_FILE in response:
                    response = response[DFU_LOGICAL_FILE][0]
                    for key in ATTRIBUTES:
                        if key in response:
                            data_dict.update({key: response[key]})
        return data_dict
    except HPCCException as e:
        raise e


def get_subfile_names(response):
    """
    Parses the Response object to get SubfileNames information

    Parameters
    ----------
    response:
        The Response object

    Returns
    -------
    pandas.Series
        A pandas series containing the SubfileNames information

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        response = response.json()
        DFU_INFO_RESPONSE = "DFUInfoResponse"
        FILE_DETAIL = "FileDetail"
        SUBFILES = "subfiles"
        ITEM = "Item"
        if DFU_INFO_RESPONSE in response:
            response = response[DFU_INFO_RESPONSE]
            if FILE_DETAIL in response:
                response = response[FILE_DETAIL]
                if SUBFILES in response:
                    response = response[SUBFILES]
                    if ITEM in response:
                        return pd.Series(response[ITEM])
    except HPCCException as e:
        raise e


def get_data_from_response(response):
    """
    Extract the content from the response

    Parameters
    ----------
    response : Response
        The Response Object

    Returns
    -------
    response: dict
        The response object with content

    """
    WU_RESULT_RESPONSE = "WUResultResponse"
    RESULT = "Result"
    ROW = "Row"
    START = "Start"
    COUNT = "Count"
    REQUESTED = "Requested"
    TOTAL = "Total"
    EXCEPTIONS = "Exceptions"
    EXCEPTION = "Exception"
    data_attr = {}
    response = response.json()

    if EXCEPTIONS in response:
        messages = []
        response = response[EXCEPTIONS]
        if EXCEPTION in response:
            for exception in response[EXCEPTION]:
                messages.append(exception["Message"])
            raise HPCCException(",".join(messages))

    if WU_RESULT_RESPONSE in response:
        response = response[WU_RESULT_RESPONSE]
        if START in response:
            data_attr.update({"start": response[START]})
        if COUNT in response:
            data_attr["count"] = response[COUNT]
        if TOTAL in response:
            data_attr["total"] = response[TOTAL]
        if REQUESTED in response:
            data_attr["requested"] = response[REQUESTED]
        if RESULT in response:
            response = response[RESULT]
            if ROW in response:
                return data_attr, response[ROW]


def get_flat_data(response):
    """
    Parses the Response to get flat data

    Parameters
    ----------
    response : Response
        Response Object

    Returns
    -------
    pandas.DataFrame
        A pandas dataframe containing the flat data

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        data_attr, data = get_data_from_response(response)
        df = pd.json_normalize(data)
        return data_attr, df
    except HPCCException as e:
        raise e


def get_csv_data(response, csv_separator, infer_headers=False, csv_headers=()):
    """
    Parses the xml response to get csv data

    Parameters
    ----------
    response : Response
        Response Object
    csv_separator : str
        The csv seperator
    csv_header : str
        The csv header

    Returns
    -------
    pandas.DataFrame
        A pandas dataframe containing the csv data

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        LINE = "line"
        csv_format_data = ""
        data_attr, rows = get_data_from_response(response)
        data_attr.pop("total")
        for row in rows:
            if LINE in row:
                csv_format_data += row[LINE] + "\n"
        csv_string = csv_format_data
        csv_format_data = StringIO(csv_format_data)
        if infer_headers:
            if csv_string == "":
                return data_attr, pd.DataFrame([], columns=csv_headers)
            return data_attr, pd.read_csv(
                csv_format_data, sep=csv_separator, names=csv_headers
            )
        else:
            if csv_string == "":
                return data_attr, pd.DataFrame()
            return data_attr, pd.read_csv(
                csv_format_data, sep=csv_separator, header=None
            )
    except HPCCException as e:
        raise e


def get_csv_header(response, csv_seperator):
    """
    Parses the header from the response

    Parameters
    ----------
    response : Response
        response with header information

    Returns
    -------
    headers: list
        List of headers
    """
    LINE = "line"
    csv_header = ""
    data_attr, rows = get_data_from_response(response)
    if data_attr["count"] == 1:
        row = rows[0]
        if LINE in row:
            csv_header = row[LINE]
            return csv_header.split(csv_seperator)


def check_file_existence(response, logical_file):
    """
    Parses the xml response to check if the file exists

    Parameters
    ----------
    response : Response
        The response object

    Returns
    -------
    bool
        False if the file does not exist, else True

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        response = response.json()
        if DFU_QUERY_RESPONSE in response:
            response = response[DFU_QUERY_RESPONSE]
            if DFU_LOGICAL_FILES in response:
                response = response[DFU_LOGICAL_FILES]
                if DFU_LOGICAL_FILE in response:
                    files = response[DFU_LOGICAL_FILE]
                    for file in files:
                        if logical_file == file["Name"]:
                            return True
        return False
    except HPCCException as e:
        raise e


# def despray_file(hpcc, query_text, cluster, jobn):
#     """
#     ToDo: Desprays a file from the HPCC cluster to the local machine

#     Parameters
#     ----------
#     hpcc : hpcc.HPCCConnection
#         The HPCC connection object
#     query_text : str
#         The query text
#     cluster : str
#         The cluster name
#     jobn : str
#         The job name

#     Returns
#     -------
#     str
#         The despray job id

#     Raises
#     ------
#     HPCCException
#         A generic exception.
#     """
#     try:
#         if hpcc is None:
#             raise HPCCException("HPCC Connection is not established")
#         if query_text is None:
#             raise HPCCException("Query text is not provided")
#         if cluster is None:
#             raise HPCCException("Cluster name is not provided")
#         if jobn is None:
#             raise HPCCException("Job name is not provided")

#         ## ToDo ##

#     except HPCCException as e:
#         raise e


def parse_bash_run_output(response: bytes):
    """
    Parse raw run output to user-friendly JSON format

    Parameters
    ----------
    response : binary string
        ecl run output

    Returns
    -------
    response: dict
        parsed run output
    """
    parsed_response = {}
    wu_info = {WUID: None, STATE: None}
    misc_info = {"message": []}
    error = {}
    messages = []
    error_messages = []
    response = response.decode()
    raw_output = response
    response = response.split("\n")
    wuid_found = False
    state_found = False
    for line in response:
        line = line.strip()
        if line == "" or re.match("|".join(RUN_UNWANTED_PATTERNS), line, re.IGNORECASE):
            continue
        if not wuid_found:
            if wuid_match := re.match(WUID_PATTERN, line):
                wu_info[WUID] = wuid_match.group(2)
                continue
        if not state_found:
            if state_match := re.match(STATE_PATTERN, line):
                wu_info[STATE] = state_match.group(2)
                continue
        if re.match("|".join(RUN_ERROR_MSG_PATTERN), line, re.IGNORECASE):
            error_messages.append(line)
            continue
        messages.append(line)
    if (
        (state_found and wu_info[STATE] in FAILED_STATUS) or wu_info[STATE] is None
    ) and len(error_messages) > 0:
        error["message"] = error_messages
        parsed_response.update(error=error)
    misc_info["message"] = messages
    parsed_response.update(raw_output=raw_output)
    parsed_response.update(wu_info=wu_info)
    parsed_response.update(misc_info=misc_info)
    return parsed_response


def parse_bash_compile_output(response, bash_command):
    """
    Parse raw compiler output to user-friendly JSON format

    Parameters
    ----------
    response : binary string
        eclcc compiler output

    Returns
    -------
    response: dict
        parsed compiler output
    """
    errors = []
    parsed_response = {}
    response = response.decode()
    raw_output = response
    response = response.split("\n")
    for line in response:
        line = line.strip()
        if line == "":
            continue

        line = line.strip()
        if re.match("|".join(COMPILE_ERROR_PATTERN), line) or re.search(
            "|".join(COMPILE_ERROR_MIDDLE_PATTERN), line
        ):
            errors.append(line)
            continue
    if len(errors) == 0:
        parsed_response["status"] = "success"
    else:
        parsed_response["status"] = "error"
        parsed_response["errors"] = errors
    parsed_response["raw_output"] = raw_output
    parsed_response["bash_command"] = bash_command
    return parsed_response
