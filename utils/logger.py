import settings

import logging


def get_logger(logger_name:str):
    """Creates a custom logger

    Args:
        logger_name (str): Unique logger name

    Returns:
        logging.Logger: logger object
    """
    logger = logging.getLogger(logger_name)
    if settings.VERBOSE:    # Activate stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(settings.STREAM_HANDLER_LOGGING_LEVEL)
        stream_formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s : %(message)s", datefmt="%d/%m/%Y %I:%M:%S %p")
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    if logger_name in settings.LOG_FILE_PATHS.keys():
        path = settings.LOG_FILE_PATHS[logger_name]
    else:
        path = settings.LOG_FILE_PATHS["DEFAULT"]
        
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(settings.FILE_HANDLER_LOGGING_LEVEL)
    file_formatter = logging.Formatter("%(asctime)s | %(levelname)s : %(message)s", datefmt="%I:%M:%S")
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger