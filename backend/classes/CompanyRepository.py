from models import CompanyModel, UserModel
from classes.User import User
from classes.Company import Company
from classes.RC import RC
from cmn_utils import *
from cmn_defs import *
from typing import List
import bcrypt
from cmn_utils import print_exception, datetime2iso, iso2datetime
from flask_sqlalchemy import SQLAlchemy
from cmn_defs import E_PERMISSIONS, E_RC
from classes.User import User
from classes.RC import RC


class CompanyRepository:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_all_companies(self) -> List[Company]:
        companies = CompanyModel.query.all()
        return [company.to_class() for company in companies]
    
    def get_all_active_companies(self) -> List[Company]:
        companies = CompanyModel.query.filter(CompanyModel.is_active == True).all()
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
    
    def create_company(self,  company_name: str) -> RC:
        try:
            new_company: Company = Company(
                company_id=None,
                company_name=company_name,
                is_active=True
            )
            
            new_company_model = new_company.to_model()

            # Add and commit using SQLAlchemy
            self.db.session.add(new_company_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"Company {company_name} created succefully!")
        
        except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def update_company(self, company: Company, company_name: str) -> RC:
        try:
            if not company:
                return RC(E_RC.RC_INVALID_INPUT, f"Company {company_name} Update failed due to invalid imput")
            
            if company_name:
                company.company_name = company_name

            company_model: CompanyModel = company.to_model()
            self.db.session.merge(company_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"Company {company_name} Updated Successfully")
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
        
    def delete_company(self, company: Company) -> RC:
        try:
            company.is_active = False
        
            company_model: CompanyModel = company.to_model()
            self.db.session.merge(company_model)
            self.db.session.commit()
            return RC(E_RC.RC_OK, f"Company {company.company_name} Deleted Successfully")
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return RC(E_RC.RC_ERROR_DATABASE, "DB Exception")
    