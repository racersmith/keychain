from anvil.server import AnvilWrappedError, _register_exception_type

class AccessDenied(AnvilWrappedError):
    None
    # message = "Access Denied"
    # def __init__(self):
    #     super().__init__(self.message)


class AlreadyRegistered(AnvilWrappedError):
    def __init__(self, key):
        super().__init__(f"'{key}' already has a registred function")
        self.key = key


_register_exception_type(f"{AccessDenied.__module__}.AccessDenied", AccessDenied)
_register_exception_type(f"{AlreadyRegistered.__module__}.AlreadyRegistered", AlreadyRegistered)
