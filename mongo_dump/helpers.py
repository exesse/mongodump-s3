import logging


def env_exists(env_variable):
    if env_variable is not None and env_variable != '':
        return True
    return False


def log():
    return logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
