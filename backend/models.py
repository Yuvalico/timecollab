# from main import db  # Import the 'db' object from your main Flask file
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, DateTime, Integer
from sqlalchemy.sql import expression
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class Company(db.Model):
    __tablename__ = 'companies'
    company_id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    company_name = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    # Define the relationship to users
    users = db.relationship('User', backref='company')

    def to_dict(self):
        return {
            'company_id': str(self.company_id),  # Convert UUID to string
            'company_name': self.company_name,
            'is_active': self.is_active
        }

class User(db.Model):
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
    employment_start = db.Column(db.DateTime(timezone=True))  # Add employment_start
    employment_end = db.Column(db.DateTime(timezone=True))    # Add employment_end
    weekend_choice = db.Column(db.String(20))              # Add weekend_choice

    def to_dict(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'mobile_phone': self.mobile_phone,
            'email': self.email,
            'company_id': str(self.company_id),
            'role': self.role,
            'permission': self.permission,
            'is_active': self.is_active,
            'salary': str(self.salary) if self.salary else None,
            'work_capacity': str(self.work_capacity) if self.work_capacity else None,
            'employment_start': self.employment_start.isoformat() if self.employment_start else None,  # Add to to_dict
            'employment_end': self.employment_end.isoformat() if self.employment_end else None,      # Add to to_dict
            'weekend_choice': self.weekend_choice                                                # Add to to_dict
        }
        
class TimeStamp(db.Model):
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
        'User',
        foreign_keys=[entered_by],
        backref='entered_timestamps'
    )

    user = db.relationship(
        'User',
        foreign_keys=[user_email],
        backref='timestamps'  # Add the backref here
    )

    @hybrid_property
    def total_work_time(self):
        if self.punch_out_timestamp and self.punch_in_timestamp:
            time_diff = self.punch_out_timestamp - self.punch_in_timestamp
            return int(time_diff.total_seconds()) 
        return None  # Or None if you prefer to handle nulls differently

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
