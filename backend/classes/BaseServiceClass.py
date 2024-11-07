from abc import ABC
from classes.BaseDomainClass import BaseDomainClass
from classes.BaseRepository import BaseRepository
from classes.BaseValidator import ValidatorInterface
from classes.DomainClassFactory import DomainClassFactory

class BaseService(ABC):
    """
    A base class for all service classes, providing common functionality 
    and promoting consistency.
    """

    def __init__(self, validator: ValidatorInterface, factory: DomainClassFactory):
        self.validator = validator
        self.factory = factory
    
    def _save(self, repository: BaseRepository, obj: BaseDomainClass):
        validation_result = self.validator.validate(obj)  
        if not validation_result.is_ok():
            return validation_result
        
        return repository.save(obj)
        
    def _update(self, repository: BaseRepository, obj: BaseDomainClass):
        validation_result = self.validator.validate(obj)  
        if not validation_result.is_ok():
            return validation_result
        
        return repository.update(obj)
        
    def _delete(self, repository: BaseRepository, obj: BaseDomainClass):
        validation_result = self.validator.validate(obj)  
        if not validation_result.is_ok():
            return validation_result
        
        return repository.delete(obj)

        

