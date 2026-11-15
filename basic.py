import logging

logger = logging.getLogger("info.txt")
logging.basicConfig(
    level=logging.INFO,
    filename='app.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
class basic_similation_element:
    def __init__(self):
        logger.info("object init: %s, id: %s info %s", self.__class__.__name__, id(self), ' '.join(self.__dir__()))

    def __del__(self):
        logger.info("object destroy: %s", self.__class__.__name__)
