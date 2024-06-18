from pyhpcc import utils


class ReadFileInfo(object):
    """
    Class to read the file information from the HPCC cluster

    Attributes
    ----------
        hpcc:
            The hpcc object
        logical_file_name:
            The logical file name
        cluster:
            The cluster to read the file information from
        file_type:
            The file type
        file_size_limit:
            The file size limit. Defaults to 25MB
        if_exists:
            Boolean to determine if the file exists
        is_superfile:
            Boolean to determine if the file is a superfile
        actual_file_size:
            The actual file size
        record_count:
            The number of records in the file
        despray_ip:
            The IP address to despray the file to
        despray_path:
            The path to despray the file to
        despray_allow_overwrite:
            Boolean to determine if the file can be overwritten. Defaults to True
        should_despray:
            Boolean to determine if the file should be desprayed. Defaults to False
        check_status:
            Boolean to determine if the file status should be checked. Defaults to False
        csv_separator_for_read:
            The csv seperator for reading the file. Defaults to ','
        read_status:
            The read status. Defaults to 'Not Read'
        despray_from_cluster:
            The cluster to despray the file from
        csv_header_flag:
            Int to determine if the file has a csv header. Defaults to 0

    Methods
    -------
        check_if_file_exists_and_is_super_file:
            Checks if the file exists and is a superfile

        set_file_name:
            Sets the logical file name

        get_sub_file_information:
            Gets the subfile information

        check_file_in_dfu:
            Checks the file in the DFU queue

        get_data:
            Gets the data from the file
    """

    def __init__(
        self,
        hpcc,
        logical_file_name,
        cluster,
        file_type,
        file_size_limit=25,
        if_exists=-1,
        is_superfile=-1,
        actual_file_size=-1,
        record_count=-1,
        despray_ip="",
        despray_path="",
        despray_allow_overwrite="true",
        should_despray=False,
        check_status=False,
        csv_separator_for_read=",",
        read_status="Not read",
        despray_from_cluster="",
        csv_header_flag=0,
    ):
        """Constructor for the ReadFileInfo class"""

        self.hpcc = hpcc
        self.logical_file_name = logical_file_name
        self.cluster = cluster
        self.file_size_limit = file_size_limit
        self.file_type = file_type
        self.if_exists = if_exists
        self.if_superfile = is_superfile
        self.actual_file_size = actual_file_size
        self.record_count = record_count
        self.despray_ip = despray_ip
        self.despray_path = despray_path
        self.despray_allow_overwrite = despray_allow_overwrite
        self.should_despray = should_despray
        self.check_status = check_status
        self.csv_separator_for_read = csv_separator_for_read
        self.read_status = read_status
        self.despray_from_cluster = despray_from_cluster
        self.csv_header_flag = csv_header_flag

    def check_if_file_exists_and_is_super_file(self, cluster_from_user):
        """Function to check if the file exists and is a superfile

        Parameters
        ----------
            cluster_from_user:
                The cluster to check the file on
        """

        self.check_status = True
        file_search = self.hpcc.file_query(
            LogicalName=self.logical_file_name,
            LogicalFileSearchType="Logical Files and Superfiles",
        )
        self.if_exists = utils.get_file_status(file_search)
        if self.if_exists != 0 and self.if_exists != "0":
            arrFESF = utils.get_file_type(file_search)
            self.cluster = (
                arrFESF["NodeGroup"]
                if arrFESF["NodeGroup"] is not None
                else cluster_from_user
            )
            self.if_super_file = (
                arrFESF["isSuperfile"] if arrFESF["isSuperfile"] is not None else ""
            )
            self.actual_file_size = (
                int(arrFESF["Totalsize"].replace(",", ""))
                if arrFESF["Totalsize"] is not None
                else ""
            )
            self.file_type = (
                arrFESF["ContentType"]
                if arrFESF["ContentType"] is not None
                else self.file_type
            )
            if bool(arrFESF):
                if arrFESF["RecordCount"] != "":
                    self.record_count = (
                        0
                        if arrFESF["RecordCount"] is None
                        else int(arrFESF["RecordCount"].replace(",", ""))
                    )
                else:
                    self.record_count = -2
        else:
            self.file_type = ""
            self.if_super_file = ""
            self.actual_file_size = None
            self.record_count = None
            self.cluster = ""
            self.read_status = "File doesn't exist"

    def set_file_name(self, file_name):
        """Function to set the logical file name and check if the file exists and is a superfile

        Parameters
        ----------
            file_name:
                The logical file name
        """
        self.logical_file_name = file_name
        self.check_if_file_exists_and_is_super_file(self.cluster)

    def get_sub_file_information(self):
        """Function to get the subfile information

        Parameters
        ----------
            None

        Returns
        -------
            subFileInformation:
                The subfile information if the file is a superfile, else returns a message "Not a superfile"
        """
        if not self.check_status:
            self.check_if_file_exists_and_is_super_file(self.cluster)
        if self.if_superfile == 1:
            sub_file_info = self.hpcc.get_subfile_info(Name=self.logical_file_name)
            return utils.get_subfile_names(sub_file_info)
        else:
            return "Not a superfile"

    def check_file_in_dfu(self):
        """Function to check if the file exists in the DFU queue

        Parameters
        ----------
            None

        Returns
        -------
            dfuFileStatus:
                A boolean to determine if the file exists in the DFU queue
        """
        status_details = self.hpcc.check_file_exists(Name=self.logical_file_name)
        status = utils.check_file_existence(status_details)
        if status == 0:
            return False
        else:
            return True

    def get_data(self):
        """Function to get the data from the file

        Parameters
        ----------
            None

        Returns
        -------
            data:
                The data from the file
        """
        self.check_if_file_exists_and_is_super_file(self.cluster)
        if self.if_exists != 0 and self.if_exists != "0":
            file_size_in_mb = (self.actual_file_size / 1024) / 1024
            if (
                file_size_in_mb > self.file_size_limit
                or self.file_type == "xml"
                or self.should_despray
            ):
                if self.despray_ip != "" and self.despray_path != "":
                    query_string = (
                        "IMPORT STD; STD.file.despray(~'"
                        + self.logical_file_name
                        + "','"
                        + self.despray_ip
                        + "','"
                        + self.despray_path
                        + "',,,,"
                        + self.despray_allow_overwrite
                        + ");"
                    )
                    cluster_from = ""
                    if self.despray_from_cluster == "":
                        cluster_from = self.cluster
                    else:
                        cluster_from = self.despray_from_cluster
                    setattr(self.hpcc, "response_type", ".json")
                    self.read_status = utils.despray_file(
                        self.hpcc,
                        query_string,
                        cluster_from,
                        "Despraying : " + self.logical_file_name,
                    )
                else:
                    self.read_status = "Unable to despray with the given input values. Please provide values for despray IP and folder"
            else:
                if self.record_count == -2:
                    count_updated = 9223372036854775807
                else:
                    count_updated = self.record_count
                    flat_csv_resp = self.hpcc.get_file_info(
                        LogicalName=self.logical_file_name,
                        Cluster=self.cluster,
                        Count=count_updated,
                    )
                    if self.file_type == "flat":
                        self.read_status = "Read"
                        return utils.get_flat_data(flat_csv_resp)
                    else:
                        self.read_status = "Read"
                        return utils.get_csv_data(
                            flat_csv_resp,
                            self.csv_separator_for_read,
                            self.csv_header_flag,
                        )
        else:
            self.read_status = "File doesn't exist"
