from models import *
from classes.dataclass.User import User
from cmn_utils import print_exception
from classes.utilities.RC import RC, E_RC
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model
from models import db
from classes.dataclass.BaseDomainClass import BaseDomainClass


class BaseRepository:
    """
    A base repository class with shared methods for database interaction.
    """
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def _save(self, model: Model) -> RC:
        """
        Saves a given model to the database.

        Args:
            model (Model): The SQLAlchemy model instance to save.

        Returns:
            RC: A result code indicating success or failure.
        """
        try:
            self.db.session.add(model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"Succefully Saved to {model.__tablename__} DB")
        except Exception as e:
            self.db.session.rollback()
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def save(self, data: BaseDomainClass) -> RC:
        """
        converts a data class to a model and saves it.

        Args:
            data (BaseDomainClass): The data class instance to convert and save.

        Returns:
            RC: A result code indicating success or failure.
        """
        try:
            if not data:
                return RC(E_RC.RC_INVALID_INPUT, "Invalid input. Input Cannot be None")
            
            new_model = data.to_model()
            return self._save(new_model)
        
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")

    def _update(self, model: Model) -> RC:
        """
        Updates a given model in the database.

        Args:
            model (Model): The SQLAlchemy model instance to update.

        Returns:
            RC: A result code indicating success or failure.
        """
        try:
            self.db.session.merge(model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"Succefully updated in {model.__tablename__} DB")  
        
        except Exception as e:
            self.db.session.rollback()
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def update(self, data: BaseDomainClass) -> RC:
        """
         converts a data class to a model and updates it.

        Args:
            data (BaseDomainClass): The data class instance to convert and update.

        Returns:
            RC: A result code indicating success or failure.
        """
        try:
            if not data:
                return RC(E_RC.RC_INVALID_INPUT, "Invalid input. Input Cannot be None")
            
            new_model = data.to_model()
            return self._update(new_model)
        
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")

    def _delete(self, model: Model) -> RC:
        """
        Deletes a given model from the database.

        Args:
            model (Model): The SQLAlchemy model instance to delete.

        Returns:
            RC: A result code indicating success or failure.
        """
        try:
            merged_obj = db.session.merge(model)
            self.db.session.delete(merged_obj)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"Succefully deleted from {model.__tablename__} DB")  
        except Exception as e:
            self.db.session.rollback()
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def delete(self, data: BaseDomainClass) -> RC:
        """
        converts a data class to a model and deletes it.

        Args:
            data (BaseDomainClass): The data class instance to convert and delete.

        Returns:
            RC: A result code indicating success or failure.
        """
        try:
            if not data:
                return RC(E_RC.RC_INVALID_INPUT, "Invalid input. Input Cannot be None")
            
            new_model = data.to_model()
            return self._delete(new_model)
        
        except Exception as e:
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")