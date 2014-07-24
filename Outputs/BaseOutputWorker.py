__author__ = 'goktan'

import abc

class BaseOutputWorker:
    __metaclass__ = abc.ABCMeta
    @abc.abstractmethod
    def generate_output(self,enriched_data,duration,theme=None):
        pass

    @abc.abstractmethod
    def save_output(self):
        pass

