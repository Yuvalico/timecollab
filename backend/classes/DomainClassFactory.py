from classes.User import User
from classes.Company import Company
from classes.TimeStamp import TimeStamp
from classes.BaseFactoryClass import BaseFactory
from classes.RC import RC, E_RC
from cmn_utils import *

class DomainClassFactory(BaseFactory):
    """
    Creates instances of domain models based on their type.
    """

    def create(self, model_type: str, **kwargs) -> User | Company | TimeStamp | RC:
        """
        Creates an instance of the specified model type.

        Args:
            model_type (str): The type of model to create ('user', 'company', 'timestamp').
            **kwargs: Keyword arguments to pass to the model constructor.

        Returns:
            User | Company | TimeStamp | None: An instance of the specified model, or None if the type is invalid.
        """
        try:
            if model_type == 'user':
                return User(**kwargs)
            elif model_type == 'company':
                return Company(**kwargs)
            elif model_type == 'timestamp':
                return TimeStamp(**kwargs)
            else:
                return RC(E_RC.RC_INVALID_INPUT, f"{model_type} is an invalid domain class type")
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_INVALID_INPUT, f"Server Error When Creating Domain Class")