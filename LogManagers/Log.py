__author__ = 'ertan'
import hoover
import logging

class Log(object):
    log = logging.getLogger('momends')

    @staticmethod
    def fatal(message):
        Log.log.fatal(message)

    @staticmethod
    def warn(message):
        Log.log.warn(message)

    @staticmethod
    def error(message):
        Log.log.error(message)

    @staticmethod
    def info(message):
        Log.log.info(message)

    @staticmethod
    def debug(message):
        Log.log.debug(message)