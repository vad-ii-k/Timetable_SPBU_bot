import logging

logging.basicConfig(
    format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    level=logging.INFO,
)

root_logger = logging.getLogger("gino")
if root_logger.level == logging.NOTSET:
    root_logger.setLevel(logging.WARN)
