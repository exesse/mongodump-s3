"""Module contains helper methods used by other modules in the package."""


def env_exists(env_variable: str) -> bool:
    """Validates if env variable was provided and is not an empty string.

    Args:
        env_variable: str, name of the env variable

    Returns:
        True: if env provide and not an empty string
        False: if env not provided or an empty string
    """
    if env_variable is not None and env_variable != '':
        return True
    return False
