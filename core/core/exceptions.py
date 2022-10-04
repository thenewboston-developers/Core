from rest_framework.exceptions import APIException


def custom_exception_handler(exc, context):
    from rest_framework.views import exception_handler  # to avoid importing it too early

    if isinstance(exc, APIException):
        # Adding machine-readable error code.
        # Original implementation copied from https://stackoverflow.com/a/50301325/1952977
        exc.detail = exc.get_full_details()

    return exception_handler(exc, context)


class NotAuthenticated(Exception):
    pass
