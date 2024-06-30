class ActionNotSupportedError(Exception):
    def __init__(self, explanation: str):
        super().__init__(explanation)
