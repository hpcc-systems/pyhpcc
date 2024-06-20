class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class HPCCAuthenticationError(Error):
    """Exception raised for HPCC authentication errors.

    Attributes:
        message:
            The error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TypeError(Error):
    """Exception raised for type errors.

    Attributes:
        message:
            The error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class HPCCException(Error):
    """Exception raised for HPCC errors.

    Attributes:
        message:
            The error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class CompileConfigException(Error):
    """Exception raised for CompileConfig Errors.

    Attributes:
        message:
            The error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class RunConfigException(Error):
    """Exception raised for RunConfig Errors

    Attributes:
        message:
            The error message
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
