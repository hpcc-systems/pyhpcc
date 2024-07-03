import re
import sys
import xml.etree.ElementTree as ET

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


def get_graph_skew(response):
    """
    Get the graph skew from the response of a WUInfo call.

    Parameters
    ----------
    response :
        str

    Returns
    -------
    dict :
        A dictionary containing the graph skew information.

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        resp_json = response.json()
        graphs = []
        xml = resp_json["WUGetGraphResponse"]["Graphs"]["ECLGraphEx"][0]["Graph"]
        root = ET.fromstringlist(xml)

        # Loop through the graph nodes and get the skew information
        for node in root.findall("./node/att/graph/node"):
            graph = {"subgraphid": node.get("id")}
            for child in node:
                if child.get("name") == "SkewMaxLocalExecute":
                    graph["skewmax"] = child.get("value")
                if child.get("name") == "TimeAvgLocalExecute":
                    graph["avgtime"] = child.get("value")
                if child.get("ecl") == "TimeAvgLocalExecute":
                    graph["ecl"] = child.get("value")
            graphs.append(graph)

        return graphs

    except HPCCException as e:
        raise e


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
    Parses the xml response to get FileType information

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
        DFU_LOGICAL_FILES = "DFULogicalFiles"
        DFU_QUERY_RESPONSE = "DFUQueryResponse"
        DFU_LOGICAL_FILE = "DFULogicalFile"
        NODE_GROUP = "NodeGroup"
        IS_SUPER_FILE = "isSuperfile"
        TOTAL_SIZE = "Totalsize"
        RECORD_COUNT = "RecordCount"
        CONTENT_TYPE = "ContentType"

        ATTRIBUTES = [NODE_GROUP, IS_SUPER_FILE, TOTAL_SIZE, RECORD_COUNT, CONTENT_TYPE]
        print(response)
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


def get_subfile_names(arg):
    """
    Parses the xml response to get SubfileNames information

    Parameters
    ----------
    arg : str
        The xml response

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
        argET = ET.fromstring(arg.content)
        subfile_name_list = []
        for child in argET:
            if child.tag == "DFUInfoResponse":
                for dfu_file in child:
                    if dfu_file.tag == "subfiles":
                        for file_info in dfu_file:
                            if file_info.tag == "Item":
                                subfile_name_list.append(file_info.text)
        return pd.Series(subfile_name_list)
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
    response = response.json()
    if WU_RESULT_RESPONSE in response:
        response = response[WU_RESULT_RESPONSE]
        if RESULT in response:
            response = response[RESULT]
            if ROW in response:
                return response[ROW]


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
        df = pd.json_normalize(get_data_from_response(response))
        return df
    except HPCCException as e:
        raise e


def get_csv_data(response, csv_separator, csv_header):
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
        rows = get_data_from_response(response)
        for row in rows:
            if LINE in row:
                csv_format_data += row[LINE] + "\n"
        csv_format_data = StringIO(csv_format_data)
        if csv_header == 0:
            return pd.read_csv(csv_format_data, sep=csv_separator, header=csv_header)
        else:
            return pd.read_csv(csv_format_data, sep=csv_separator, header=None)
    except HPCCException as e:
        raise e


def check_file_existence(arg):
    """
    Parses the xml response to check if the file exists

    Parameters
    ----------
    arg : str
        The xml response

    Returns
    -------
    int
        0 if the file does not exist, else a positive integer

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        argET = ET.fromstring(arg.content)
        i = 0
        for child in argET:
            if child.tag == "Prefix":
                if child.text is None:
                    i += 0
                else:
                    i += 1
            if child.tag == "NodeGroup":
                if child.text is None:
                    i += 0
                else:
                    i += 1
            if child.tag == "Owner":
                if child.text is None:
                    i += 0
                else:
                    i += 1
            if child.tag == "FileType":
                if child.text is None:
                    i += 0
                else:
                    i += 1
            if child.tag == "StartDate":
                if child.text is None:
                    i += 0
                else:
                    i += 1
        return i
    except HPCCException as e:
        raise e


def despray_file(hpcc, query_text, cluster, jobn):
    """
    ToDo: Desprays a file from the HPCC cluster to the local machine

    Parameters
    ----------
    hpcc : hpcc.HPCCConnection
        The HPCC connection object
    query_text : str
        The query text
    cluster : str
        The cluster name
    jobn : str
        The job name

    Returns
    -------
    str
        The despray job id

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        if hpcc is None:
            raise HPCCException("HPCC Connection is not established")
        if query_text is None:
            raise HPCCException("Query text is not provided")
        if cluster is None:
            raise HPCCException("Cluster name is not provided")
        if jobn is None:
            raise HPCCException("Job name is not provided")

        ## ToDo ##

    except HPCCException as e:
        raise e


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


def parse_bash_compile_output(response):
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
    return parsed_response
