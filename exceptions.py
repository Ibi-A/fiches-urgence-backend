class InvalidRequestException(Exception):
    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = f"Invalid request: {message}"
        self.status_code = status_code
