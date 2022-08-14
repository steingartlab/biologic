class ECLibException(Exception):
    """Base exception for all ECLib exceptions"""
    def __init__(self, message, error_code):
        super(ECLibException, self).__init__(message)
        self.error_code = error_code

    def __str__(self):
        """__str__ representation of the ECLibException"""
        string = '{} code: {}. Message \'{}\''.format(
            self.__class__.__name__,
            self.error_code,
            self.message)
        return string

    def __repr__(self):
        """__repr__ representation of the ECLibException"""
        return self.__str__()

class ECLibError(ECLibException):
    """Exception for ECLib errors"""
    def __init__(self, message, error_code):
        super(ECLibError, self).__init__(message, error_code)

class ECLibCustomException(ECLibException):
    """Exceptions that does not originate from the lib"""
    def __init__(self, message, error_code):
        super(ECLibCustomException, self).__init__(message, error_code)