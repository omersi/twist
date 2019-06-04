import logging


def create_logger():
    """
    Creates a logging object and returns it
    """
    logger = logging.getLogger("get_credentials_from_dynamo_db")
    logger.setLevel(logging.INFO)

    # create the logging file handler
    fh = logging.FileHandler(r"/var/log/get_credentials_from_dynamo_db.log")

    fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(fmt)
    fh.setFormatter(formatter)

    # add handler to logger object
    logger.addHandler(fh)
    return logger


logger = create_logger()
