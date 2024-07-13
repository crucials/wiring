class MissingEnvironmentVariablesError(Exception):
    """environment variables that required to run certain tests are missing

    check the error message in string representation:
        `str(missing_environment_variables_error)`
    """
