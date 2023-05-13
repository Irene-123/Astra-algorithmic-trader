class CredentialsNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        """Database credentials does not exist
        """
        super().__init__(*args)

class FailedConnectionException(Exception):
    def __init__(self, *args: object) -> None:
        """Database could not be connected
        """
        super().__init__(*args)

class QueryFailedException(Exception):
    def __init__(self, *args: object) -> None:
        """Query did not execute successfully
        """
        super().__init__(*args)