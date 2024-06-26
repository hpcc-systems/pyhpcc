import logging

import pyhpcc.config as conf
from pyhpcc.errors import HPCCAuthenticationError
from pyhpcc.utils import convert_arg_to_utf8_str

log = logging.getLogger(__name__)


def roxie_handler(**config):
    """
    Decorator for HPCC Roxie class methods.

    Parameters
    ----------
    config : dict
        A dictionary of configuration options for HPCC Roxie class methods.

    Returns
    -------
    function
        The decorated function

    Raises
    ------
    TypeError
        If the config parameter is not a dictionary
    """

    class APIMethod(object):
        api = config["api"]
        response_type = api.response_type
        method = config.get("method", "POST")
        require_auth = config.get("require_auth", False)
        use_cache = config.get("use_cache", True)

        def __init__(self, args, kwargs):
            """
            Constructor for the HPCC Roxie APIMethod class.

            Parameters
            ----------
            args : list
                The positional arguments

            kwargs : dict
                The keyword arguments

            Returns
            -------
            None
            """
            api = self.api
            self.session = api.auth.session
            if self.require_auth and not api.auth:
                raise HPCCAuthenticationError("Authentication required for this method")
            self.post_data = kwargs.pop("data", None)
            self.session.headers = kwargs.pop("headers", {})
            self.build_parameters(args, kwargs)

        def build_parameters(self, args, kwargs):
            """
            Builds the parameters for the API call

            Parameters:
            ----------
                args:
                    The positional arguments
                kwargs:
                    The keyword arguments

            Returns:
            -------
                A dictionary of parameters

            Raises:
            ------
                TypeError:
                    If the parameter is not allowed or if duplicate parameters are passed

            """
            self.session.params = {}
            for idx, arg in enumerate(args):
                if arg is None:
                    continue
                try:
                    self.session.params[self.allowed_param[idx]] = (
                        convert_arg_to_utf8_str(arg)
                    )
                except Exception:
                    raise TypeError("Too many arguments")
            for k, arg in list(kwargs.items()):
                # for k, arg in kwargs.items():
                if arg is None:
                    continue
                if k in self.session.params:
                    raise TypeError("Duplicate argument: %s" % k)

                self.session.params[k] = convert_arg_to_utf8_str(arg)

            log.info("PARAMS: %r", self.session.params)

        def execute(self):
            """
            Executes the API call

            Parameters:
            ----------
                None

            Returns:
            -------
                The response from the API call

            Raises:
            ------
                requests.HTTPError:
                    If the response is not OK
            """
            self.api.cached_result = False

            # Build the request URL
            full_url = (
                self.api.auth.get_url()
                + self.api.auth.path_delimiter
                + self.api.definition
                + self.api.auth.path_delimiter
                + self.api.roxie_port
                + self.api.auth.path_delimiter
                + self.api.search_service
                + self.api.auth.path_delimiter
                + "."
                + self.response_type
            )

            # Debugging
            if conf.DEBUG:
                print("full_url: ", full_url)
                print("self.session.params: ", self.session.params)
                print("self.session.headers: ", self.session.headers)
                print("self.post_data: ", self.post_data)

            # If auth is required, add auth to the session
            if self.api.auth:
                auth = self.api.auth.oauth

            # Execute request
            resp = self.session.request(
                self.method,
                full_url,
                data=self.post_data,
                timeout=self.api.timeout,
                auth=auth,
            )

            # Check for errors
            self.api.last_response = resp
            resp.raise_for_status()

            result = resp

            # Cache the result
            # if self.use_cache and self.api.cache:
            #     self.api.cache.set(self.session.params, result)

            return result

    def _call(*args, **kwargs):
        """
        Calls the API method

        Parameters
        ----------
        args : list
            The positional arguments

        kwargs : dict
            The keyword arguments

        Returns
        -------
        object
            The result of the API call

        """
        method = APIMethod(args, kwargs)
        return method.execute()

    return _call
