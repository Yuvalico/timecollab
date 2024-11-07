from abc import ABC, abstractmethod
from classes.RC import RC

class ValidatorInterface(ABC):
    """
    An interface for validator classes, defining the required methods.
    """

    @abstractmethod
    def validate(self, obj: object) -> RC:
        """
        Validates the given object.

        Args:
            obj (BaseModel): The object to validate.

        Returns:
            RC: A result code indicating success or failure with a message.
        """
        pass