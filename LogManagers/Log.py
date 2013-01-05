__author__ = 'ertan'
import hoover
import logging

class Log(object):
    handler = hoover.LogglyHttpHandler(token='ef2e6682-a591-4eef-a81c-34c91854c314')
    log = logging.getLogger('momends')
    log.addHandler(handler)

    @staticmethod
    def info(message):
        Log.log.info(message)

    @staticmethod
    def error(message):
        Log.log.error(message)

    @staticmethod
    def debug(message):
        Log.log.debug(message)