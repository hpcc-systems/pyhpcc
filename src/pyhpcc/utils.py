import sys
import xml.etree.ElementTree as ET

import pandas as pd
import six

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
from pyhpcc.command_config import CompileConfig
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


def get_file_status(arg):
    """
    Parses the xml response to get NumFiles information

    Parameters
    ----------
    arg : str
        The xml response

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
        root = ET.fromstring(arg)
        for child in root:
            if child.tag == "NumFiles":
                return child.text

    except HPCCException as e:
        raise e


def get_file_type(arg):
    """
    Parses the xml response to get FileType information

    Parameters
    ----------
    arg : str
        The xml response

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
        argET = ET.fromstring(arg.content)
        data_dict = {}

        # Loop through the xml and get the FileType information
        for child in argET:
            if child.tag == "DFULogicalFiles":
                for dfu_file in child:
                    if dfu_file.tag == "DFULogicalFile":
                        for fileinfo in dfu_file:
                            if fileinfo.tag == "NodeGroup":
                                data_dict.update({fileinfo.tag: fileinfo.text})
                            if fileinfo.tag == "isSuperfile":
                                data_dict.update({fileinfo.tag: fileinfo.text})
                            if fileinfo.tag == "Totalsize":
                                data_dict.update({fileinfo.tag: fileinfo.text})
                            if fileinfo.tag == "RecordCount":
                                data_dict.update({fileinfo.tag: fileinfo.text})
                            if fileinfo.tag == "ContentType":
                                data_dict.update({fileinfo.tag: fileinfo.text})
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


def get_flat_data(arg):
    """
    Parses the xml response to get flat data

    Parameters
    ----------
    arg : str
        The xml response

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
        list_dict = []
        argET = ET.fromstring(arg.content)
        for child in argET:
            if child.tag == "Result":
                for child in child:
                    if child.tag == "Dataset":
                        for row in child:
                            data_dict = {}
                            for row_data in row:
                                data_dict[row_data.tag] = row_data.text
                            list_dict.append(data_dict)
        return pd.DataFrame(list_dict)
    except HPCCException as e:
        raise e


def get_csv_data(arg, csv_separator, csv_header):
    """
    Parses the xml response to get csv data

    Parameters
    ----------
    arg : str
        The xml response
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
        argET = ET.fromstring(arg.content)
        list_dict = []
        for child in argET:
            if child.tag == "Result":
                for child in child:
                    if child.tag == "Dataset":
                        for row in child:
                            data_dict = {}
                            for row_data in row:
                                data_dict[row_data.tag] = row_data.text + "\n"
                            list_dict.append(data_dict)
        xml_str = ""
        for each_dict in list_dict:
            for key, value in list(each_dict.items()):
                if key == "line":
                    if "None" in str(value):
                        xml_str = xml_str
                    else:
                        xml_str = xml_str + str(value)
        csv_format_data = StringIO(xml_str)
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
