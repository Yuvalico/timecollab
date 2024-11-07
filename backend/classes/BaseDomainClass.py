from abc import ABC, abstractmethod

class BaseDomainClass(ABC):
    @abstractmethod
    def to_dict(self):
        pass

    @abstractmethod
    def to_model(self):
        pass