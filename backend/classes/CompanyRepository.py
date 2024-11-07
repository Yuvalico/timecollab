from models import CompanyModel, UserModel
from classes.User import User
from classes.Company import Company
from classes.RC import RC
from cmn_utils import *
from typing import List
import bcrypt
from cmn_utils import print_exception, datetime2iso, iso2datetime
from flask_sqlalchemy import SQLAlchemy
from classes.User import User
from classes.RC import RC, E_RC
from classes.BaseRepository import BaseRepository
from classes.Permission import E_PERMISSIONS



class CompanyRepository(BaseRepository):
    def __init__(self, db: SQLAlchemy):
        super().__init__(db)

    def get_all_companies(self) -> List[Company]:
        companies = CompanyModel.query.all()
        return [company.to_class() for company in companies]
    
    def get_all_active_companies(self) -> List[Company]:
        companies = CompanyModel.query.filter(CompanyModel.is_active == True).all()
        return [company.to_class() for company in companies]
    
    def get_all_inactive_companies(self) -> List[Company]:
        companies = CompanyModel.query.filter(CompanyModel.is_active == False).all()
        return [company.to_class() for company in companies]
    
    def get_company_admins(self, company_id: str) -> List[User]:
        if not company_id:
            return []
        
        admins = UserModel.query.filter(UserModel.company_id == company_id, UserModel.permission.in_([E_PERMISSIONS.employer, E_PERMISSIONS.net_admin]), 
                        UserModel.is_active == True ).all()
        
        return [admin.to_class() for admin in admins]

    def get_company_by_id(self, company_id: str) -> Company | RC:
        company = CompanyModel.query.get(company_id)
        if company:
            return company.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"Company {company_id} not found")
    
    def get_company_by_name(self, company_name: str) -> Company:
        company: CompanyModel = CompanyModel.query.filter_by(company_name=company_name).first()
        if company:
            return company.to_class()
        return RC(E_RC.RC_NOT_FOUND, f"Company {company_name} not found")
    
    def get_company_users(self, company_id: str) -> List[User]:
        users: UserModel = UserModel.query.filter_by(company_id=company_id, is_active=True).all()
        if users:
            return [user.to_class() for user in users]
        return []
    
    # def create_company(self,  new_company: Company) -> RC:
    #     try:
    #         new_company_model = new_company.to_model()

    #         return self._save(new_company_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def update_company(self, company: Company) -> RC:
    #     try:
    #         if not company:
    #             return RC(E_RC.RC_INVALID_INPUT, f"Company {company.company_name} Update failed due to invalid imput")
            
    #         company_model: CompanyModel = company.to_model()
    #         return self._update(company_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    # def delete_company(self, company: Company) -> RC:
    #     try:
    #         company.is_active = False
        
    #         company_model: CompanyModel = company.to_model()
    #         return self._delete(company_model)
        
    #     except Exception as e:
    #         print_exception(e)
    #         return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
    