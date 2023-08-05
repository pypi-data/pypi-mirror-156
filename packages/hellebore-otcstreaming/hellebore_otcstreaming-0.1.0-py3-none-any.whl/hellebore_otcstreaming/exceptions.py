class OTCException(Exception):
    """Global class for exceptions of the library."""

    def __init__(self, message):
        super(Exception, self).__init__(message)


class RequestFailedException(OTCException):
    """Raised when a request fails where it should not"""

    def __init__(self, code, message):
        """Initialize the exception."""
        self.message = message
        self.code = code

    def __str__(self):
        return f"""Request failed with code {self.code} : {self.message}"""
