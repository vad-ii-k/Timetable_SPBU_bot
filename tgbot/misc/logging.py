import logging

logging.basicConfig(
    format="%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s",
    level=logging.INFO,
)

root_logger = logging.getLogger("gino")
if root_logger.level == logging.NOTSET:
    root_logger.setLevel(logging.WARN)
