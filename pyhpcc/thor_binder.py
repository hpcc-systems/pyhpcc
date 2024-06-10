import re
import requests
import logging 
from pyhpcc.errors import HPCCAuthenticationError, TypeError
from pyhpcc.utils import convert_arg_to_utf8_str
import pyhpcc.config as conf

log = logging.getLogger(__name__)


def wrapper(**config):
    """Decorator for HPCC THOR class methods.

    Parameters
    ----------
    config : dict
        A dictionary of configuration options for HPCC THOR class methods.

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
        api = config['api'] 
        path = config['path']
        response_type = api.response_type
        payload_list = config.get('payload_list', False)
        allowed_param = config.get('allowed_param', [])
        method = config.get('method', 'POST')
        require_auth = config.get('require_auth', True)
        use_cache = config.get('use_cache', True)
        
        def __init__(self, args, kwargs):
            """
            Constructor for the HPCC THOR APIMethod class.

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
                raise HPCCAuthenticationError('Authentication required for this method')
            self.data = kwargs.pop('data', None)
            self.files = kwargs.pop('files', None)
            self.session.headers = kwargs.pop('headers', {})
            self.build_payload(args, kwargs)
        

        def build_payload(self, args, kwargs):
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

            for key, arg in enumerate(args):
                if arg is None:
                    continue
                try:
                    self.session.params[self.allowed_param[key]] = convert_arg_to_utf8_str(arg)
                except:
                    raise TypeError('Too many arguments')
                
            for key, arg in kwargs.items():
                if arg is None:
                    continue
                if key in self.session.params:
                    raise TypeError('Duplicate argument: %s' % key)

                try:
                    self.session.params[key] = convert_arg_to_utf8_str(arg)
                except IndexError:
                    raise TypeError('Too many arguments')
            
            log.info('Parameters: %s' % self.session.params)

        
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

            # if self.use_cache and self.api.cache:
            #     result = self.api.cache.get(self.session.params)
            #     if result:
            #         self.api.cached_result = True
            #         return result
            
            full_url = self.api.auth.get_url() + self.path + "."+  self.response_type

            # Debugging
            if conf.DEBUG:
                print("full_url: ", full_url)
                print("self.session.params: ", self.session.params)
                print("self.session.headers: ", self.session.headers)
                print("self.session.data: ", self.data)
                print("self.session.files: ", self.files)

            self.session.headers['Accept_Encoding'] = 'gzip'

            # If auth is required, add auth to the session
            if self.api.auth:
                auth = self.api.auth.oauth
            
            resp = self.session.request(self.method,
                                        full_url,
                                        data=self.data,
                                        files=self.files,
                                        timeout = self.api.timeout,
                                        auth=auth)
            
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

