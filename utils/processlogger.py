import logging


class ProcessLogger:
    def __init__(self):
        self.__logger = logging.getLogger('__name__')
        self.__logger.handlers.clear()
        self.__logger.propagate = False

        self.__logger.setLevel(logging.DEBUG)

        fmt = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s'
        )

        fh = logging.FileHandler('../info.log')
        fh.setFormatter(fmt)

        sh = logging.StreamHandler()
        sh.setFormatter(fmt)

        self.__logger.addHandler(fh)
        self.__logger.addHandler(sh)

    def info(self, message):
        self.__logger.info(message)

    def critical(self, message):
        self.__logger.critical(message)

    def warning(self, message):
        self.__logger.warning(message)

    def debug(self, message):
        self.__logger.debug(message)

    def test(self, test_name):
        self.__logger.debug('=============END TEST {}=============\n'.format(test_name))


if __name__ == '__main__':
    open('../info.log', 'w').close()
