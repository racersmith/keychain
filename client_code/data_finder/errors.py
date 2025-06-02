class AccessDenied(Exception):
    message = "Access Denied"
    def __init__(self):
        super().__init__(self.message)


class AlreadyRegistered(Exception):
    def __init__(self, key):
        super().__init__(f"'{key}' already has a registred function")
        self.key = key