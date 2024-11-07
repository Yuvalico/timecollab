from classes.dataclass.Company import Company
from classes.utilities.RC import RC
from cmn_utils import *
from flask_sqlalchemy import SQLAlchemy
from classes.repositories.CompanyRepository import CompanyRepository
from classes.utilities.Permission import Permission
from classes.services.BaseServiceClass import BaseService
from classes.validators.ModelValidator import ModelValidator
from classes.factories.DomainClassFactory import DomainClassFactory

class CompanyService(BaseService):
    def __init__(self, company_repository: CompanyRepository, validator: ModelValidator, factory: DomainClassFactory):
        super().__init__(validator, factory)
        self.company_repository = company_repository

    def create_company(self, company_name: str, user_permission: int) -> RC:
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        if not company_name:
            return RC(E_RC.RC_INVALID_INPUT, "Missing company name")
        
        existing_company = self.company_repository.get_company_by_name(company_name=company_name)
        if not isinstance(existing_company, RC):
            return RC(E_RC.RC_INVALID_INPUT, "Company already exists")
        
        new_company_data: dict = {
                'company_id': None,
                'company_name': company_name,
                'is_active': True
                }
        
        new_company: Company = self.factory.create("company", **new_company_data)
        if isinstance(new_company, RC):
            return new_company
        
        return self._save(self.company_repository, new_company)

    def update_company(self, company_id: str, company_name: str, user_permission: int) -> RC:
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        if not company_name:
            return RC(E_RC.RC_INVALID_INPUT, "Missing company name")
                
        company: Company | RC = self.company_repository.get_company_by_id(company_id)
        if isinstance(company, RC):
            return company  

        company.company_name = company_name
        
        return self._update(self.company_repository, company)  

    def delete_company(self, company_id: str, user_permission: int) -> RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        
        company = self.company_repository.get_company_by_id(company_id)
        if isinstance(company, RC):
            return RC(E_RC.RC_NOT_FOUND, 'Company not found')

        company.is_active = False
        
        return self._update(self.company_repository, company)

    def get_active_companies(self, user_permission: int) -> list:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        active_companies = self.company_repository.get_all_active_companies()

        # Format the results
        company_data = []
        for company in active_companies:
            company_dict = company.to_dict()
            admins = self.company_repository.get_company_admins(company.company_id)
            company_dict['admin_user'] = admins[0].to_dict() if admins else None
            company_data.append(company_dict)

        return company_data

    def get_all_companies(self, user_permission: int) -> list:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if not perm.is_net_admin():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        all_companies = self.company_repository.get_all_companies()

        # Format the results
        company_data = []
        for company in all_companies:
            company_dict = company.to_dict()
            admins = self.company_repository.get_company_admins(company.company_id)
            company_dict['admin_user'] = admins[0].to_dict() if admins else None
            company_data.append(company_dict)

        return company_data

    def get_company_users(self, company_id: str, user_permission: int, user_company_id) -> list:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        if perm.is_employee():
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        company = self.company_repository.get_company_by_id(company_id=company_id)
        if isinstance(company, RC):
            return company

        if perm.is_employer() and company.company_id != user_company_id:
            return RC(E_RC.RC_UNAUTHORIZED, "Unauthorized access")
        
        users = self.company_repository.get_company_users(company_id=company_id)
        return [user.to_dict() for user in users]

    def get_company_details(self, company_id: str, user_company_id: str, user_permission: int) -> dict | RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        company: Company = self.company_repository.get_company_by_id(company_id=company_id)
        if isinstance(company, RC):
            return company

        company_dict = company.to_dict()
        if perm.is_net_admin():
            return company_dict

        if user_company_id == company_id:
            if perm.is_employer():
                return company_dict
            else:
                return {'company_name': company.company_name}
        else:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized access')

    def get_company_admins(self, company_id: str, user_company_id: str, user_permission: int) -> list | RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        company = self.company_repository.get_company_by_id(company_id)
        if isinstance(company, RC):
            return company

        if perm.is_employee():
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized to access this information')

        if perm.is_employer() and user_company_id != company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized to access this information')

        admins = self.company_repository.get_company_admins(company_id)
        return [admin.to_dict() for admin in admins]

    def get_company_name_by_id(self, company_id: str, user_company_id: str, user_permission: int) -> dict | RC:
        
        perm: Permission = Permission(user_permission)
        if isinstance(perm, RC):
            return perm
        
        company = self.company_repository.get_company_by_id(company_id)
        if isinstance(company, RC):
            return company

        if perm.is_employee() and user_company_id != company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized to access this information')

        if perm.is_employer() and user_company_id != company_id:
            return RC(E_RC.RC_UNAUTHORIZED, 'Unauthorized to access this information')

        return {'company_name': company.company_name}