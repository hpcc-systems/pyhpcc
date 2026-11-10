"""PEP 249 exception hierarchy for the HPCC SQL driver."""


class Warning(Exception):
    """Exception raised for important warnings."""


class Error(Exception):
    """Base class for database errors."""


class InterfaceError(Error):
    """Exception raised for errors related to the database interface."""


class DatabaseError(Error):
    """Exception raised for database errors."""


class DataError(DatabaseError):
    """Exception raised for errors processing data."""


class OperationalError(DatabaseError):
    """Exception raised for database operation failures."""


class IntegrityError(DatabaseError):
    """Exception raised for relational integrity failures."""


class InternalError(DatabaseError):
    """Exception raised for internal database failures."""


class ProgrammingError(DatabaseError):
    """Exception raised for invalid SQL or arguments."""


class NotSupportedError(DatabaseError):
    """Exception raised for unsupported database features."""


class TimeoutError(OperationalError):
    """Exception raised when a query exceeds its timeout."""
