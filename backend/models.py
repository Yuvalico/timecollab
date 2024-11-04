from dataclasses import dataclass
from datetime import datetime
from typing import List
import bcrypt
from cmn_utils import print_exception
# from main import db  # Import the 'db' object from your main Flask file
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime, Integer
from sqlalchemy.sql import expression
from sqlalchemy.ext.hybrid import hybrid_property
from cmn_defs import E_PERMISSIONS

db = SQLAlchemy()

@dataclass
class Company:
    company_id: str
    company_name: str
    is_active: bool
    
    def to_dict(self):
        return {
            'company_id': str(self.company_id),  # Convert UUID to string
            'company_name': self.company_name,
            'is_active': self.is_active
        }
    def to_model(self):
        return CompanyModel(
            company_id = self.company_id if self.company_id else None,  # Convert UUID to string
            company_name = self.company_name,
            is_active = self.is_active
        )

@dataclass
class User:
    email: str
    first_name: str
    last_name: str
    mobile_phone: str
    company_id: str
    role: str
    permission: int
    pass_hash: str
    is_active: bool
    salary: float  # You might want to use the Salary value object here
    work_capacity: float
    employment_start: datetime
    employment_end: datetime
    weekend_choice: str
    
    def to_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'mobile_phone': self.mobile_phone,
            'company_id': str(self.company_id),  # Convert UUID to string
            'role': self.role,
            'permission': self.permission,
            # Exclude 'pass_hash' for security reasons
            'is_active': self.is_active,
            'salary': str(self.salary) if self.salary else None,  # Handle potential None values
            'work_capacity': str(self.work_capacity) if self.work_capacity else None,
            'employment_start': self.employment_start.isoformat() if self.employment_start else None,
            'employment_end': self.employment_end.isoformat() if self.employment_end else None,
            'weekend_choice': self.weekend_choice
        }
        
    def to_model(self):
        return UserModel(
            email= self.email,
            first_name= self.first_name,
            last_name= self.last_name,
            mobile_phone= self.mobile_phone,
            company_id= self.company_id,  # Convert UUID to string
            role= self.role,
            permission= self.permission,
            pass_hash = self.pass_hash,
            is_active= self.is_active,
            salary= float(self.salary) if self.salary else 0,  
            work_capacity= float(self.work_capacity) if self.work_capacity else 0,
            employment_start = self.employment_start,
            employment_end = self.employment_end,
            weekend_choice = self.weekend_choice
        )

@dataclass
class TimeStamp:
    uuid: str
    user_email: str
    entered_by: str
    punch_type: int
    punch_in_timestamp: datetime
    punch_out_timestamp: datetime
    reporting_type: str
    detail: str
    total_work_time: int
    last_update: datetime

    def calculate_total_work_time(self) -> int:
        if self.punch_out_timestamp and self.punch_in_timestamp:
            time_diff = self.punch_out_timestamp - self.punch_in_timestamp
            return int(time_diff.total_seconds())
        return 0
    
    def to_dict(self):
        return {
            'uuid': str(self.uuid),
            'user_email': str(self.user_email),
            'entered_by': str(self.entered_by),
            'punch_type': self.punch_type,
            'punch_in_timestamp': self.punch_in_timestamp.isoformat() if self.punch_in_timestamp else None,
            'punch_out_timestamp': self.punch_out_timestamp.isoformat() if self.punch_out_timestamp else None,
            'reporting_type': self.reporting_type,
            'detail': self.detail,
            'total_work_time': self.total_work_time,
            'last_update': self.last_update.isoformat() if self.last_update else None,
        }
        
    def to_model(self):
        return TimeStampModel(
            uuid =  UUID(self.uuid) if self.uuid else None,
            user_email =  self.user_email,
            entered_by =  self.entered_by,
            punch_type =  self.punch_type,
            punch_in_timestamp =  datetime.fromisoformat(self.punch_in_timestamp.replace('Z', '+00:00')) if self.punch_in_timestamp else None,
            punch_out_timestamp =  datetime.fromisoformat(self.punch_out_timestamp.replace('Z', '+00:00')) if self.punch_out_timestamp else None,
            reporting_type =  self.reporting_type,
            detail =  self.detail,
            total_work_time =  self.total_work_time,
            last_update =  self.last_update.isoformat() if self.last_update else None,
        )


class CompanyModel(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    company_name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    # Define the relationship to users
    users = db.relationship('UserModel', backref='company')

    def to_class(self):
        return Company(
            company_id=str(self.company_id),
            company_name=self.company_name,
            is_active=self.is_active
        )

class UserModel(db.Model):
    __tablename__ = 'users'
    email = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    mobile_phone = db.Column(db.String(20))
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('companies.company_id'))
    role = db.Column(db.String(255))
    permission = db.Column(db.Integer)
    pass_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    salary = db.Column(db.Numeric)
    work_capacity = db.Column(db.Numeric)
    employment_start = db.Column(db.DateTime(timezone=True))
    employment_end = db.Column(db.DateTime(timezone=True))
    weekend_choice = db.Column(db.String(20))

    def to_class(self):
        return User(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            mobile_phone=self.mobile_phone,
            company_id=str(self.company_id),  # Convert UUID to string
            role=self.role,
            permission=self.permission,
            pass_hash=self.pass_hash,
            is_active=self.is_active,
            salary=float(self.salary) if self.salary is not None else None,
            work_capacity=float(self.work_capacity) if self.work_capacity is not None else None,
            employment_start=self.employment_start,
            employment_end=self.employment_end,
            weekend_choice=self.weekend_choice
        )
        
class TimeStampModel(db.Model):
    __tablename__ = 'time_stamps'
    uuid = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
    user_email = db.Column(db.ForeignKey('users.email'),nullable=False)
    entered_by = db.Column(db.ForeignKey('users.email'), nullable=False)
    punch_type = db.Column(db.Integer)
    punch_in_timestamp = db.Column(db.DateTime(timezone=True))
    punch_out_timestamp = db.Column(db.DateTime(timezone=True))
    reporting_type = db.Column(db.String)
    detail = db.Column(db.Text)
    total_work_time = db.Column(db.Integer, nullable=True) 
    last_update = db.Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=expression.text('CURRENT_TIMESTAMP AT TIME ZONE \'UTC\'')
    )

    entered_by_user = db.relationship(
        'UserModel',
        foreign_keys=[entered_by],
        backref='entered_timestamps'
    )

    user = db.relationship(
        'UserModel',
        foreign_keys=[user_email],
        backref='timestamps'  # Add the backref here
    )

    @hybrid_property
    def total_work_time(self):
        if self.punch_out_timestamp and self.punch_in_timestamp:
            time_diff = self.punch_out_timestamp - self.punch_in_timestamp
            return int(time_diff.total_seconds()) 
        return None 

    def to_class(self):
        return TimeStamp(
            uuid=str(self.uuid),
            user_email=self.user_email,
            entered_by=self.entered_by,
            punch_type=self.punch_type,
            punch_in_timestamp=self.punch_in_timestamp,
            punch_out_timestamp=self.punch_out_timestamp,
            reporting_type=self.reporting_type,
            detail=self.detail,
            total_work_time=self.total_work_time,
            last_update=self.last_update,
        )


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
        
        admins = db.session.query(UserModel).filter_by(is_active=True, company_id = company_id, permission= E_PERMISSIONS.employer).all()
        return [admin.to_class() for admin in admins]

    def get_company_by_id(self, company_id: str) -> Company:
        company = CompanyModel.query.get(company_id)
        if company:
            return company.to_class()
        return None
    
    def get_company_by_name(self, company_name: str) -> Company:
        company: CompanyModel = CompanyModel.query.filter_by(company_name=company_name).first()
        if company:
            return company.to_class()
        return None
    
    def get_company_users(self, company_id: str) -> List[User]:
        users: UserModel = UserModel.query.filter_by(company_id=company_id, is_active=True).all()
        if users:
            return [user.to_class() for user in users]
        return []
    
    def create_company(self,  company_name: str) -> bool:
        try:
            new_company: Company = Company(
                company_id=None,
                company_name=company_name,
                is_active=True
            )
            
            new_company_model = Company.to_model()

            # Add and commit using SQLAlchemy
            self.db.session.add(new_company_model)
            self.db.session.commit()
            return True
        
        except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return False
        
    def update_company(self, company: Company, company_name: str) -> bool:
        try:
            if not company:
                return False
            
            if company_name:
                company.weekend_choice = company_name

            company_model: CompanyModel = company.to_model()
            self.db.session.merge(company_model)
            self.db.session.commit()
            return True
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return False
        
    def delete_company(self, company: Company) -> bool:
        try:
            company.is_active = False
        
            company_model: CompanyModel = company.to_model()
            self.db.session.merge(company_model)
            self.db.session.commit()
            return True
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return False
    
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

    def get_user_by_email(self, email: str) -> User:
        user: UserModel = UserModel.query.get(email)
        if user:
            return user.to_class()
        return None
    
    def create_user(self, email: str, first_name: str, last_name: str, company_id: str,\
        role: str, permission: int, password: str, salary: float, work_capacity: float,\
            employment_start_str: str, employment_end_str: str, weekend_choice: str, mobile_phone: str = None) -> User:
        # Create new user object
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
                employment_start=datetime.fromisoformat(employment_start_str.replace('Z', '+00:00')) if employment_start_str else None,
                employment_end=datetime.fromisoformat(employment_end_str.replace('Z', '+00:00')) if employment_end_str else None,
                weekend_choice=weekend_choice,
                mobile_phone=mobile_phone
            )
            
            new_user_model = new_user.to_model()

            # Add and commit using SQLAlchemy
            self.db.session.add(new_user_model)
            self.db.session.commit()
            return new_user
        
        except Exception as e:
            self.db.session.rollback()  
            print_exception(e)
            return False
        
    def update_user(self, user: User, first_name: str= None, last_name: str= None, company_id: str= None,\
        role: str= None, permission: int= None, mobile_phone: str= None, password: str= None, salary: float= None, work_capacity: float= None,\
            employment_start_str: str= None, employment_end_str: str= None, weekend_choice: str = None) -> bool:
        try:
            if not user:
                return False
            
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
                employment_start = datetime.fromisoformat(employment_start_str.replace('Z', '+00:00')) if employment_start_str else None
                user.employment_start = employment_start
            if employment_end_str:
                employment_end = datetime.fromisoformat(employment_end_str.replace('Z', '+00:00')) if employment_end_str else None
                user.employment_end = employment_end
            if weekend_choice:
                user.weekend_choice = weekend_choice
            
            if password:
                user.pass_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            user_model: UserModel = user.to_model()
            self.db.session.merge(user_model)
            self.db.session.commit()
            return True
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return False
        
    def delete_user(self, user: User, employment_end_str: str= None) -> bool:
        try:
            user.is_active = False
            user.employment_end = datetime.fromisoformat(employment_end_str.replace('Z', '+00:00'))  # Set employment_end
        
            user_model: UserModel = user.to_model()
            self.db.session.merge(user_model)
            self.db.session.commit()
            return True
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return False
        
    def change_password(self, user: User, password: str= None) -> bool:
        try:
            
            user.pass_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user_model: UserModel = user.to_model()
            self.db.session.merge(user_model)
            self.db.session.commit()
            return True
        
        except Exception as e:
            self.db.session.rollback() 
            print_exception(e)
            return False
    
class TimeStampRepository:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def get_all_timestamps(self) -> List[TimeStamp]:
        timestamps = TimeStampModel.query.all()
        return [timestamp.to_class() for timestamp in timestamps]

    def get_timestamp_by_uuid(self, uuid: str) -> TimeStamp:
        timestamp = TimeStampModel.query.get(uuid)
        if timestamp:
            return timestamp.to_class()
        return None
    
    def create_timestamp(self, email, entered_by_user, punch_type, punch_in_timestamp, reporting_type, detail) -> TimeStamp:
        new_timestamp = TimeStamp(
                user_email=user.email,
                entered_by=entered_by_user,
                punch_type=punch_type,
                punch_in_timestamp=punch_in_timestamp,
                reporting_type=reporting_type,
                detail=detail
            )
        new_timestamp_model = new_timestamp.to_model()

            # Add and commit using SQLAlchemy
            self.db.session.add(new_user_model)
            self.db.session.commit()
            return new_user
        
        if timestamp:
            return timestamp.to_class()
        return None
    