from models import *
from classes.User import User
from typing import List
import bcrypt
from cmn_utils import print_exception, datetime2iso, iso2datetime
from cmn_defs import *
from classes.User import User
from classes.RC import RC


class UserRepository:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_all_active_users(self, company_id: str = None) -> List[User]:
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
    
    def get_active_users(self, company_id: str = None) -> List[User]:
        if not company_id:
            active_users: list[User] = (
                self.db.session.query(User, Company)
                .filter(User.is_active == True)
                .all()
            )
        else:
            active_users: list[User] = (
                self.db.session.query(User, Company)
                .filter(
                    User.is_active == True,  # Filter for active users
                    User.company_id == company_id  # Filter by the employer's company_id
                )
                .all()
            )
         
        return [user.to_class() for user in active_users]

    def get_user_by_email(self, email: str) -> User | RC:
        user: UserModel = UserModel.query.get(email)
        if user:
            return user.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"User not found for id: {email}'")
    
    def create_user(self, email: str, first_name: str, last_name: str, company_id: str,\
        role: str, permission: int, password: str, salary: float, work_capacity: float,\
            employment_start_str: str, employment_end_str: str, weekend_choice: str, mobile_phone: str = None) -> RC:
        
        try:
            new_user: User = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                company_id=company_id,  # Associate with the company
                role=role,
                permission=permission,
                pass_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
                is_active=True,
                salary=salary,
                work_capacity=work_capacity,
                employment_start=iso2datetime(employment_start_str),
                employment_end=iso2datetime(employment_end_str),
                weekend_choice=weekend_choice,
                mobile_phone=mobile_phone
            )
            
            new_user_model = new_user.to_model()

            # Add and commit using SQLAlchemy
            self.db.session.add(new_user_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"User {new_user.email} created succesfully!")
        
        except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def update_user(self, user: User, first_name: str= None, last_name: str= None, company_id: str= None,\
        role: str= None, permission: int= None, mobile_phone: str= None, password: str= None, salary: float= None, work_capacity: float= None,\
            employment_start_str: str= None, employment_end_str: str= None, weekend_choice: str = None) -> RC:
        try:
            if not user:
                return RC(E_RC.RC_INVALID_INPUT, "No user query received")
            
            if first_name:
                user.first_name = first_name
            if last_name:
                user.last_name = last_name
            if mobile_phone:
                user.mobile_phone = mobile_phone
            if role:
                user.role = role
            if permission:
                user.permission = permission
            if salary:
                user.salary = salary
            if work_capacity:
                user.work_capacity = work_capacity
            if employment_start_str:
                employment_start = iso2datetime(employment_start_str)
                user.employment_start = employment_start
            if employment_end_str:
                employment_end = iso2datetime(employment_end_str)
                user.employment_end = employment_end
            if weekend_choice:
                user.weekend_choice = weekend_choice
            
            if password:
                user.pass_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            user_model: UserModel = user.to_model()
            self.db.session.merge(user_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"User {user.email} updated succesfully")
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def delete_user(self, user: User, employment_end_str: str= None) -> RC:
        try:
            user.is_active = False
            user.employment_end = iso2datetime(employment_end_str)
        
            user_model: UserModel = user.to_model()
            self.db.session.merge(user_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"User {user.email} Deleted Succefully!")
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def change_password(self, user: User, password: str= None) -> RC:
        try:
            user.pass_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_model: UserModel = user.to_model()
            self.db.session.merge(user_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"User {user.email} password updated successfuly!")
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")