class CredentialsNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        """Broker credentials does not exist
        """
        super().__init__(*args)

class FailedLoginException(Exception):
    def __init__(self, *args: object) -> None:
        """Broker login unsuccessful
        """
        super().__init__(*args)

class InvalidPropertyTypeException(Exception):
    def __init__(self, *args: object) -> None:
        """Scrip property does not exist
        """
        super().__init__(*args)

class PropertyValueNotFoundException(Exception):
    def __init__(self, *args: object) -> None:
        """Property value does not exist for any scrip
        """
        super().__init__(*args)