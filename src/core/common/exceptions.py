from fastapi import HTTPException as FastAPIHttpException
from fastapi import status


class HTTPException(FastAPIHttpException):
    pass


class NotFoundException(HTTPException):
    def __init__(self, message: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message)


class BadRequestException(HTTPException):
    def __init__(self, message: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message)


class UnauthorizedException(HTTPException):
    def __init__(self, message: str = "Unauthorized Exception"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


class ConflictException(HTTPException):
    def __init__(self, message: str = "Conflict Exception"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message)


class ShortCodeAlreadyExistsError(ConflictException):
    def __init__(self, message: str = "Short code already exists"):
        super().__init__(message=message)
