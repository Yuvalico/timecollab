from abc import ABC, abstractmethod

class BaseFactory(ABC):
    """
    An interface for model factory classes.
    """

    @staticmethod
    @abstractmethod
    def create(type: str, **kwargs) -> object | None:
        """
        Creates an instance of the specified model type.

        Args:
            model_type (str): The type of model to create.
            **kwargs: Keyword arguments to pass to the model constructor.

        Returns:
            BaseModel | None: An instance of the specified model, or None if the type is invalid.
        """
        pass