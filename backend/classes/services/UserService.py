from classes.dataclass.User import User
from cmn_utils import *
import bcrypt
from classes.validators.ModelValidator import ModelValidator
from classes.repositories.UserRepository import UserRepository
from classes.repositories.CompanyRepository import CompanyRepository
from classes.factories.DomainClassFactory import DomainClassFactory
from classes.dataclass.Company import Company
from classes.utilities.Permission import Permission
from classes.utilities.RC import RC, E_RC
from classes.services.BaseServiceClass import BaseService


class UserService(BaseService):
    def __init__(self, user_repository: UserRepository, company_repository: CompanyRepository, validator: ModelValidator, factory: DomainClassFactory):
        super().__init__(validator, factory)
        self.user_repository = user_repository
        self.company_repository = company_repository

    def create_user(self, email: str, first_name: str, last_name: str, company_name: str,
                   role: str, permission: int, password: str, salary: float, work_capacity: float,
                   employment_start_str: str, user_permission: int,
                   mobile_phone: str = None, employment_end_str: str = None, weekend_choice: str = None) -> RC:

        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        if not first_name or not last_name or not email or not password or not company_name\
            or not role or not permission or not salary or not work_capacity or not employment_start_str:
                return RC(E_RC.RC_INVALID_INPUT, "Missing mandatory user field")
            
        # Check if company exists
        company: Company = self.company_repository.get_company_by_name(company_name)
        if isinstance(company, RC):
            return company  # Return error if company not found

        # Check if user already exists
        existing_user: User | RC = self.user_repository.get_user_by_email(email)
        if not isinstance(existing_user, RC):
            return RC(E_RC.RC_INVALID_INPUT, 'User email already exists')

        # Create new user object
        user_data = {
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'company_id': company.company_id, 
            'role': role,
            'permission': permission,
            'pass_hash': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            'is_active': True,
            'salary': float(salary),
            'work_capacity': float(work_capacity),
            'employment_start': iso2datetime(employment_start_str),
            'employment_end': iso2datetime(employment_end_str),
            'weekend_choice': weekend_choice,
            'mobile_phone': mobile_phone
            }
        new_user: User = self.factory.create("user", **user_data)
        if isinstance(new_user, RC):
            return new_user

        return self._save(self.user_repository, new_user)

    def update_user(self, user_email: str, user_permission: int, first_name: str = None, last_name: str = None,
                    company_id: str = None, role: str = None, permission: int = None,
                    mobile_phone: str = None, password: str = None, salary: float = None,
                    work_capacity: float = None, employment_start_str: str = None,
                    employment_end_str: str = None, weekend_choice: str = None) -> RC:

        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if company_id:
            user.company_id = company_id
        if role:
            user.role = role
        if permission is not None:
            user.permission = permission
        if mobile_phone:
            user.mobile_phone = mobile_phone
        if password:
            user.pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        if salary is not None:
            user.salary = float(salary)
        if work_capacity is not None:
            user.work_capacity = float(work_capacity)
        if employment_start_str:
            user.employment_start = iso2datetime(employment_start_str)
        if employment_end_str:
            user.employment_end = iso2datetime(employment_end_str)
        if weekend_choice:
            user.weekend_choice = weekend_choice

        return self._update(self.user_repository, user)


    def delete_user(self, user_permission, user_email: str, employment_end_str: str = None) -> RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user
        
        #soft delete
        user.is_active = False
        user.employment_end = iso2datetime(employment_end_str)
        
        return self._update(self.user_repository, user)

    def change_password(self, user_permission: int, current_user_email: str, current_user_company: int, user_email: str, new_password: str) -> RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        user: User | RC = self.user_repository.get_user_by_email(user_email)
        if isinstance(user, RC):
            return user
        
        if perm.is_net_admin() or \
            (perm.is_employer() and current_user_company == user.company_id) or \
                (perm.is_employee() and current_user_email == user.email):
                    
            user.pass_hash=bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return self._update(self.user_repository, user)
        
        return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
    
    def reactivate_user(self, user_permission: int, user_to_reactivate_email: str) -> RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
            
        user: User | RC = self.user_repository.get_user_by_email(user_to_reactivate_email)
        if isinstance(user, RC):
            return user
        
        user.is_active = True
        user.employment_end = None
        
        return self._update(self.user_repository, user)

    def get_user_by_email(self, user_permission: int, current_user_email: str, user_company_id, requested_user_email: str) -> RC|dict:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        requested_user: User = self.user_repository.get_user_by_email(requested_user_email)
        
        if perm.is_employer():
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            if user_company_id != requested_user.company_id:
                return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
            
        if perm.is_employee() and current_user_email and current_user_email != requested_user.email:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        return requested_user.to_dict()
    
    def get_active_users(self, user_permission: int, user_company_id: str = None) -> list:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_net_admin():
            active_users: list[User] = self.user_repository.get_active_users()
        elif perm.is_employer:
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            
            active_users: list[User] = self.user_repository.get_active_users(user_company_id)
        else:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        user_data = []
        for user in active_users:
            user_dict = user.to_dict()
            user_dict['company_name'] = self.company_repository.get_company_by_id(user.company_id).company_name
            user_data.append(user_dict)

        return user_data
    
    def get_inactive_users(self, user_permission: int, user_company_id: str = None) -> list:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_net_admin():
            active_users: list[User] = self.user_repository.get_inactive_users()
        elif perm.is_employer:
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            
            active_users: list[User] = self.user_repository.get_inactive_users(user_company_id)
        else:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        user_data = []
        for user in active_users:
            user_dict = user.to_dict()
            user_dict['company_name'] = self.company_repository.get_company_by_id(user.company_id).company_name
            user_data.append(user_dict)

        return user_data

    def get_all_users(self, user_permission: int, user_company_id: str = None) -> list:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_net_admin:
            users: list[User] = self.user_repository.get_users()  
            
        elif perm.is_employer():
            if not user_company_id:
                return RC(E_RC.RC_INVALID_INPUT, "No user company id found")
            users: list[User] = self.user_repository.get_active_users(user_company_id)
        else:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")

        user_data = []
        for user in users:
            user_dict = user.to_dict()
            user_dict['company_name'] = self.company_repository.get_company_by_id(user.company_id).company_name
            user_data.append(user_dict)

        return user_data