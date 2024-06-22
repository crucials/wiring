from typing import Optional

from multi_platform_resources import Platform


class BotApiError(Exception):
    """
    common class that represents an error occurred on some platform
    api interaction

    ...
    """
    def __init__(self, platform: Platform, explanation: Optional[str] = None,
                 status_code: Optional[int] = None):
        error_text = f'failed to perform some action through {platform} api'

        if explanation is not None:
            error_text = explanation

        if status_code is not None:
            error_text += f'. status code: {status_code}'

        super().__init__(error_text)
