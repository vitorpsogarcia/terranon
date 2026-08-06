class SingletonException(Exception):
    """Exception raised when trying to create a second instance of a singleton class."""

    def __init__(self, message="This class is a singleton!"):
        self.message = message
        super().__init__(self.message)
