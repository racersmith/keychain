from anvil.server import AnvilWrappedError, _register_exception_type


class AccessDenied(AnvilWrappedError):
    None


class AlreadyRegistered(AnvilWrappedError):
    def __init__(self, key):
        super().__init__(f"'{key}' already has a registred function")
        self.key = key


class ServerRedirect(AnvilWrappedError):
    def __init__(self, path, data=None):
        self.path = path
        self.data = data

_register_exception_type(f"{AccessDenied.__module__}.AccessDenied", AccessDenied)
_register_exception_type(
    f"{AlreadyRegistered.__module__}.AlreadyRegistered", AlreadyRegistered
)
