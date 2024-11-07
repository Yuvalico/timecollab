from datetime import datetime, timezone
from typing import List
from cmn_utils import print_exception, datetime2iso, iso2datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime
from sqlalchemy.sql import expression
from sqlalchemy.ext.hybrid import hybrid_property
from classes.dataclass.User import User
from classes.dataclass.Company import Company
from classes.dataclass.TimeStamp import TimeStamp
from abc import ABC, abstractmethod

db = SQLAlchemy()
class ModelInterface():
    @abstractmethod
    def to_class(self):
        raise NotImplementedError
    
class CompanyModel(db.Model, ModelInterface):
    __tablename__ = 'companies'
    company_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())
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

class UserModel(db.Model, ModelInterface):
    __tablename__ = 'users'
    email = db.Column(db.String(255), primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    mobile_phone = db.Column(db.String(11))
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('companies.company_id'))
    role = db.Column(db.String(255))
    permission = db.Column(db.Integer)
    pass_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    salary = db.Column(db.Numeric)
    work_capacity = db.Column(db.Numeric)
    employment_start = db.Column(db.DateTime(timezone=True))
    employment_end = db.Column(db.DateTime(timezone=True))
    weekend_choice = db.Column(db.String(64))

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
            weekend_choice=self.weekend_choice,
            company=self.company.to_class(),
        )
        
class TimeStampModel(db.Model, ModelInterface):
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
            user = self.user.to_class()
        )
