default_error_msg = 'The error message is unknown, because it is the '\
                    'method to retrieve the error message with that fails. '\
                    'See the error codes sections (5.4) of the EC-Lab '\
                    'development package documentation to get the meaning '\
                    'of the error code.'


class ECLibException(Exception):
    """Base exception for all ECLib exceptions"""

    def __init__(self, error_code: int, message: str = None):
        super(ECLibException, self).__init__(message)

        self.error_code: int = error_code
        self.message: str = default_error_msg if message is None else message

    def __str__(self):
        """__str__ representation of the ECLibException"""

        return f'{self.__class__.__name__}\nerror code: {self.error_code}\nmessage: "{self.message}"'

    def __repr__(self):
        """__repr__ representation of the ECLibException"""

        return self.__str__()


class ECLibError(ECLibException):
    """Exception for ECLib errors"""

    def __init__(self, error_code: int, message: str):
        super(ECLibError, self).__init__(
            error_code=error_code, message=message
            )


class BLFindError(ECLibException):

    def __init__(self, error_code: int, message: str):
        super(BLFindError, self).__init__(
            error_code=error_code, message=message
            )


class ECLibCustomException(ECLibException):
    """Exceptions that does not originate from the lib"""

    def __init__(self, error_code: int, message: str = None):

        super(ECLibCustomException, self).__init__(
            error_code=error_code, message=message
            )
