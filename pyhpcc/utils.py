import six
import xml.etree.ElementTree as ET
import pandas as pd
import sys

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO
import six
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


def create_compile_bash_command(repository, outputfile, filename):
    """
    Create a bash command to compile a file.

    Parameters
    ----------
    repository : str
        The repository to compile the file from.
    outputfile : str
        The output file to write the compiled code to.
    filename : str
        The filename to compile.

    Returns
    -------
    str
        The bash command to compile the file.

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        return """ eclcc -legacy  -I {0}  -platform=thor  -E -o {1} {2} -wu""".format(
            repository, outputfile, filename
        )
    except HPCCException as e:
        raise e


def create_compile_file_name(filename):
    """
    Create a compiled file name from a filename.

    Parameters
    ----------
    filename : str
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
        return filename.split(".")[0] + ".eclxml"
    except HPCCException as e:
        raise e


def create_run_bash_command(
    compiledfile, cluster, ip, port, username, password, jobname
):
    """
    Create a bash command to run a compiled file.

    Parameters
    ----------
    compiledfile : str
        The compiled file to run.
    cluster : str
        The cluster to run the compiled file on.
    ip : str
        The ip address of the HPCC cluster.
    port : str
        The port of the HPCC cluster.
    username : str
        The username to use to connect to the HPCC cluster.
    password : str
        The password to use to connect to the HPCC cluster.
    jobname : str
        The name of the job to run.

    Returns
    -------
    str
        The bash command to run a compiled file.

    Raises
    ------
    HPCCException
        A generic exception.
    """
    try:
        return """ecl run {0} --limit=100 --wait=0 --target={1}  --server={2} --ssl --port={3} -u={4} -pw={5} --name={6} -v""".format(
            compiledfile, cluster, ip, port, username, password, jobname
        )
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


def getfileStatus(arg):
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


def getfileType(arg):
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
                for dfufile in child:
                    if dfufile.tag == "DFULogicalFile":
                        for fileinfo in dfufile:
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


def getSubfileNames(arg):
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
        subfilenamelist = []
        for child in argET:
            if child.tag == "DFUInfoResponse":
                for dfufile in child:
                    if dfufile.tag == "subfiles":
                        for fileinfo in dfufile:
                            if fileinfo.tag == "Item":
                                subfilenamelist.append(fileinfo.text)
        return pd.Series(subfilenamelist)
    except HPCCException as e:
        raise e


def getflatdata(arg):
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
                            for rowdata in row:
                                data_dict[rowdata.tag] = rowdata.text
                            list_dict.append(data_dict)
        return pd.DataFrame(list_dict)
    except HPCCException as e:
        raise e


def getcsvdata(arg, csvSeperator, csvHeader):
    """
    Parses the xml response to get csv data

    Parameters
    ----------
    arg : str
        The xml response
    csvSeperator : str
        The csv seperator
    csvHeader : str
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
                            for rowdata in row:
                                data_dict[rowdata.tag] = rowdata.text + "\n"
                            list_dict.append(data_dict)
        xmlstr = ""
        for eachdict in list_dict:
            for key, value in list(eachdict.items()):
                if key == "line":
                    if "None" in str(value):
                        xmlstr = xmlstr
                    else:
                        xmlstr = xmlstr + str(value)
        csvformatdata = StringIO(xmlstr)
        if csvHeader == 0:
            return pd.read_csv(csvformatdata, sep=csvSeperator, header=csvHeader)
        else:
            return pd.read_csv(csvformatdata, sep=csvSeperator, header=None)
    except HPCCException as e:
        raise e


def checkfileexistence(arg):
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


def desprayfile(hpcc, querytext, Cluster, jobn):
    """
    ToDo: Desprays a file from the HPCC cluster to the local machine

    Parameters
    ----------
    hpcc : hpcc.HPCCConnection
        The HPCC connection object
    querytext : str
        The query text
    Cluster : str
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
        if querytext is None:
            raise HPCCException("Query text is not provided")
        if Cluster is None:
            raise HPCCException("Cluster name is not provided")
        if jobn is None:
            raise HPCCException("Job name is not provided")

        ## ToDo ##

    except HPCCException as e:
        raise e
