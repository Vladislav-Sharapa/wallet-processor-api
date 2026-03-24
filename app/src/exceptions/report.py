from fastapi import status
from app.src.core.exceptions import BaseHttpApplicationException


class NoDataForCreatingReport(BaseHttpApplicationException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "There is no data for creating report"


class NoDataToRecordInStorage(BaseHttpApplicationException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "No file to record in storage"


class NoDataFromServerException(BaseHttpApplicationException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to return data from server"


class TaskNotExistOrProcessedException(BaseHttpApplicationException):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "The task does not exist or is being processed"


class FileNotBelongsToUserException(BaseHttpApplicationException):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "The requested file does not belongs to user"
