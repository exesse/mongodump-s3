import logging


def env_exists(env_variable):
    if env_variable is not None and env_variable != '':
        return True
    return False


def log(level='INFO'):
    severity = f'logging.{level}'
    return logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=severity)
