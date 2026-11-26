class ApplicationException(Exception):
    def __init__(
        self,
        message: str = "Something went wrong."
        "Try later or send this message to support",
    ):
        self.message = message
        super().__init__(self.message)
