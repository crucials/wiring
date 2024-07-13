class UnusableBotError(Exception):
    """bot account you're running cant be used for testing

    perhaps your bot account lacks some resources or permissions required when
    testing
    
    check the error message in string representation: `str(unusable_bot_error)`
    """
    pass
