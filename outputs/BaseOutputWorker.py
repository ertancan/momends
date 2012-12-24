__author__ = 'goktan'

import abc

class BaseOutputWorker:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def generate_output(self):
        pass

    @abc.abstractmethod
    def _save_output(self):
        pass

