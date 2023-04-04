import logging

# Create and configure logger
logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def log(func):
    def handler(*args, **kwargs):
        func_name = func.__name__
        try:
            res = func(*args, **kwargs)
            logger.info(f"{func_name} has been processed")
            return res
        except Exception as e:
            logger.error(e)
            raise e
    return handler
