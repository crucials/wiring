from wiring.errors.bot_api_error import BotApiError
from wiring.multi_platform_resources import Platform


class NotFoundError(BotApiError):
    """resource cant be found on some platform

    subclass of `BotApiError`
    """
    def __init__(self, platform: Platform, explanation: str):
        super().__init__(platform, explanation, 404)
