from pyhpcc.handlers.thor_handler import roxie_wrapper


class Roxie(object):
    """
    Base class for HPCC Roxie API

    Attributes
    ----------
        auth:
            Authentication object
        timeout:
            Timeout for requests
        response_type:
            Type of response to return
        definition:
            Definition of the API
        search_service:
            Search service object
        roxie_port:
            Roxie port

    Methods
    -------
        __init__(auth, timeout, response_type, definition, search_service, roxie_port)
            Initialize the class

        roxie_call(self)
            Call the roxie API
    """

    def __init__(
        self,
        auth,
        search_service,
        roxie_port,
        timeout=1200,
        response_type="json",
        definition="submit",
    ):
        self.auth = auth
        self.timeout = timeout
        self.response_type = response_type
        self.definition = "WsEcl/" + definition + "/query"
        self.search_service = search_service
        self.roxie_port = roxie_port

    @property
    def roxie_call(self):
        """Call the roxie API

        Parameters
        ----------
            self:
                The object pointer

        Returns
        -------
            response:
                The response from the API

        """
        return roxie_wrapper(api=self)
