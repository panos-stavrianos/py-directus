from http import HTTPStatus


class ApiException(Exception):
    def __init__(self, message: str = "", extras: dict = None, status_code: HTTPStatus = HTTPStatus.NOT_ACCEPTABLE):
        self.status_code = status_code
        self.message = message
        self.extras = extras

    def __str__(self):
        return self.message
