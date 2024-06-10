import requests
from pyhpcc.errors import HPCCAuthenticationError


class auth(object):
    """Base class for HPCC authentication

    Attributes:
    ----------
        ip:
            The IP address of the HPCC instance
        port:
            The port of the HPCC instance
        username:
            The username for the HPCC instance
        password:
            The password for the HPCC instance
        require_auth:
            Boolean value to determine if authentication is required
        protocol:
            The protocol to use for the HPCC instance
        oauth:
            The OAuth credentials
        session:
            The session object
        portDelimiter:
            The delimiter for the port
        pathDelimiter:
            The delimiter for the path
        hostDelimiter:
            The delimiter for the host

    Methods:
    -------
        get_url:
            Returns a URL for the HPCC instance
        get_username:
            Returns the username
        get_verified:
            Make a request to the HPCC API to verify the credentials
    """

    def __init__(
        self, ip, port, username, password, require_auth=True, protocol="https"
    ):
        self.portDelimiter = ":"
        self.pathDelimiter = "/"
        self.hostDelimiter = "://"
        self.ip = ip
        self.port = str(port)
        self.username = username
        self.password = password
        self.require_auth = require_auth
        self.protocol = protocol
        self.oauth = (self.username, self.password)
        self.session = requests.Session()

    def get_url(self):
        """
        Returns a URL for the HPCC instance

        Parameters:
        ----------
            None

        Returns:
        -------
            The URL

        Raises:
        ------
            None
        """
        url = (
            self.protocol
            + self.hostDelimiter
            + self.ip
            + self.portDelimiter
            + self.port
        )
        return url

    def get_username(self):
        """
        Returns the username

        Parameters:
        ----------
            None

        Returns:
        -------
            The username

        Raises:
        ------
            None
        """
        return self.username

    def get_verified(self):
        """
        Make a request to the HPCC API to verify the credentials

        Parameters:
        ----------
            None

        Returns:
        -------
            Boolean value to determine if the credentials are valid

        Raises:
        ------
            HPCCAuthenticationError: For any errors with the authentication
        """
        try:
            if self.require_auth:
                with self.session as s:
                    response = s.get(url=self.get_url(), auth=self.oauth)
                    if response.status_code == 200:
                        return True
                    else:
                        raise HPCCAuthenticationError(response)
            else:
                with self.session as s:
                    response = s.get(url=self.get_url())
                    if response.status_code == 200:
                        return True
                    else:
                        raise HPCCAuthenticationError(response)

        except Exception as e:
            raise HPCCAuthenticationError(e)
