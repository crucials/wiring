from typing import Optional

from multi_platform_resources import Platform


class BotApiError(Exception):
    """
    common class that represents an http error occurred on some platform
    api interaction

    Attributes:
        status_code: http error status code
    """
    def __init__(self, platform: Platform, explanation: Optional[str] = None,
                 status_code: Optional[int] = None):
        """creates common http error that occurred on some platform api interaction

        Args:
            status_code: http error status code
        """

        error_text = f'failed to perform some action through {platform} api'

        if explanation is not None:
            error_text = explanation

        if status_code is not None:
            error_text += f'. status code: {status_code}'

        super().__init__(error_text)
