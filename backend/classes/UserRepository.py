from models import *
from classes.User import User
from typing import List
from cmn_utils import print_exception, datetime2iso, iso2datetime
from classes.User import User
from classes.RC import RC, E_RC
from classes.BaseRepository import BaseRepository


class UserRepository(BaseRepository):
    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def get_active_users(self, company_id: str = None) -> List[User]:
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .filter(UserModel.is_active == True)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(UserModel, CompanyModel)
                .filter(
                    UserModel.is_active == True,  # Filter for active users
                    CompanyModel.company_id == company_id  # Filter by the employer's company_id
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]
    
    def get_inactive_users(self, company_id: str = None) -> List[User]:
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .filter(UserModel.is_active == False)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(UserModel, CompanyModel)
                .filter(
                    UserModel.is_active == False,  # Filter for active users
                    CompanyModel.company_id == company_id  # Filter by the employer's company_id
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]
    
    def get_users(self, company_id: str = None) -> List[User]:
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(UserModel)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(UserModel, CompanyModel)
                .filter(
                    CompanyModel.company_id == company_id  # Filter by the employer's company_id
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]

    def get_user_by_email(self, email: str) -> User | RC:
        user: UserModel = UserModel.query.get(email)
        if user:
            return user.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"User not found for id: {email}'")
    
    # def create_user(self, new_user: User) -> RC:
        
    #     try:
    #         new_user_model = new_user.to_model()

    #         return self._save(new_user_model)
            
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def update_user(self, user: User) -> RC:
    #     try:
    #         if not user:
    #             return RC(E_RC.RC_INVALID_INPUT, "No user query received")
            
    #         user_model: UserModel = user.to_model()
    #         return self._update(user_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def delete_user(self, user: User) -> RC:
    #     try:
            
    #         user_model: UserModel = user.to_model()
    #         return self._delete(user_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def change_password(self, user: User) -> RC:
    #     try:
    #         user_model: UserModel = user.to_model()
    #         return self._update(user_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")