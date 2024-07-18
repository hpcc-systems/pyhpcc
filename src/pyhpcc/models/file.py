from pyhpcc import utils
from pyhpcc.models.hpcc import HPCC


class ReadFileInfo(object):
    """
    Class to read the file information from the HPCC cluster

    Attributes
    ----------
        hpcc:
            The hpcc object
        logical_file_name:
            The logical file name
        csv_separator_for_read:
            The csv seperator for reading the file. Defaults to ','
        infer_header:
            bool varialbe if the header to be inferred from csv file

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

        get_data_iter:
            Get batch_size data from the file
    """

    def __init__(
        self,
        hpcc: HPCC,
        logical_file_name,
        infer_header=True,
        csv_separator_for_read=",",
    ):
        """Constructor for the ReadFileInfo class"""

        self.hpcc = hpcc
        self.logical_file_name = logical_file_name
        self.cluster = ""
        self.file_type = ""
        self.if_exists = -1
        self.if_superfile = False
        self.actual_file_size = -1
        self.record_count = -1
        self.check_status = False
        self.csv_separator_for_read = csv_separator_for_read
        self.read_status = "Not read"
        self.infer_header = infer_header

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
            self.if_superfile = (
                arrFESF["isSuperfile"] if "isSuperfile" in arrFESF else False
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
                        9223372036854775807
                        if arrFESF["RecordCount"] is None
                        else int(arrFESF["RecordCount"].replace(",", ""))
                    )
                else:
                    self.record_count = -2
        else:
            self.file_type = ""
            self.if_superfile = False
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
        if self.if_superfile:
            sub_file_info = self.hpcc.get_subfile_info(Name=self.logical_file_name)
            return self.if_superfile, utils.get_subfile_names(sub_file_info)
        else:
            return self.if_superfile, None

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
        status_details = self.hpcc.check_file_exists(LogicalName=self.logical_file_name)
        return utils.check_file_existence(status_details, self.logical_file_name)

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
                        flat_csv_resp, self.csv_separator_for_read
                    )
        else:
            raise FileNotFoundError("Logical File Not found")

    def get_data_iter(self, start_index, items_size, batch_size):
        """Function to get the data from the file

        Parameters
        ----------
        start_index : int
            start index of the data
        items_size: int
            Total count of the items to retrieve
        batch_size: int
            Number of items to retrieve per call


        Returns
        -------
            data: pd.DataFrame
                The data from the file
        """
        MAX_ITEMS = 9223372036854775807
        self.check_if_file_exists_and_is_super_file(self.cluster)
        file_name = self.logical_file_name
        file_attributes: dict = {
            "record_count": self.record_count,
            "cluster": self.cluster,
            "if_exists": self.if_exists,
            "file_type": self.file_type,
        }
        if file_attributes["if_exists"] != 0 and file_attributes["if_exists"] != "0":
            csv_header = []
            if file_attributes["file_type"] == "csv" and self.infer_header:
                start_index = max(1, start_index)
                header_response = self.hpcc.get_file_info(
                    LogicalName=file_name,
                    Cluster=file_attributes["cluster"],
                    Start=0,
                    Count=1,
                )
                csv_header = utils.get_csv_header(
                    header_response, self.csv_separator_for_read
                )
            if items_size == -1:
                items_size = MAX_ITEMS
            end_index = start_index + items_size
            while start_index < end_index:
                curr_chunk_size = min(end_index - start_index, batch_size)
                self.read_status = "Read"
                resp = self.hpcc.get_file_info(
                    LogicalName=file_name,
                    Cluster=file_attributes["cluster"],
                    Start=start_index,
                    Count=curr_chunk_size,
                )
                if file_attributes["file_type"] == "flat":
                    data_attr, df = utils.get_flat_data(resp)
                else:
                    data_attr, df = utils.get_csv_data(
                        resp,
                        self.csv_separator_for_read,
                        self.infer_header,
                        csv_header,
                    )
                if data_attr["count"] == 0:
                    return
                start_index = start_index + batch_size
                yield data_attr, df
        else:
            raise FileNotFoundError("Logical File Not found")
