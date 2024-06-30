from wiring.multi_platform_resources import Platform


class NotMessageableChatError(Exception):
    def __init__(self, platform: Platform, chat_id=None):
        if chat_id is not None:
            super().__init__(f'cant send message in chat \'{chat_id}\' on {platform}')
        else:
            super().__init__(f'cant send message in specified chat on {platform}')
