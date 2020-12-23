"""Helper module contains functions need by mongo-dump package."""

import logging


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


def log() -> None:
    """Setups logging to stdout with logging level INFO."""
    return logging.basicConfig(
        format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
