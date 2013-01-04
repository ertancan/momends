__author__ = 'ertan'
import hoover
import logging

class Loggly(object):
    handler = hoover.LogglyHttpHandler(token='ef2e6682-a591-4eef-a81c-34c91854c314')
    log = logging.getLogger('momends')
    log.addHandler(handler)

    @staticmethod
    def info(message):
        Loggly.log.setLevel(logging.INFO)
        Loggly.log.info(message)

    @staticmethod
    def error(message):
        Loggly.log.setLevel(logging.ERROR)
        Loggly.log.error(message)

    @staticmethod
    def debug(message):
        Loggly.log.setLevel(logging.DEBUG)
        Loggly.log.debug(message)