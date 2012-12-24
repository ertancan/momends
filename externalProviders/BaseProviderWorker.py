__author__ = 'goktan'

import abc

class BaseProviderWorker:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def collect_data(self):
        pass

    def auth(self):
        pass

