from abc import ABCMeta, abstractmethod


class PreprocessingInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def preprocess(self, phrase):
        pass
