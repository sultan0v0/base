from src.core.exceptions.base import ApplicationException


class NotFoundException(ApplicationException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(message)


class ConflictException(ApplicationException):
    def __init__(self, message: str = "Data Conflict"):
        super().__init__(message)


class ForbiddenException(ApplicationException):
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message)


class NotAuthenticatedException(ApplicationException):
    def __init__(self, message: str = "Not Authenticated"):
        super().__init__(message)


class BadRequestException(ApplicationException):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(message)
