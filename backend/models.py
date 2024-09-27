# from main import db  # Import the 'db' object from your main Flask file
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy

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
    id = db.Column(UUID(as_uuid=True), primary_key=True, server_default=func.uuid_generate_v4())

    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    mobile_phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('companies.company_id'))
    role = db.Column(db.String(255))
    permission = db.Column(db.Integer)
    pass_hash = db.Column(db.String(255))
    is_active = db.Column(db.Boolean)
    salary = db.Column(db.Numeric)
    work_capacity = db.Column(db.Numeric)

    def to_dict(self):
        return {
            'id': str(self.id),  # Convert UUID to string
            'first_name': self.first_name,
            'last_name': self.last_name,
            'mobile_phone': self.mobile_phone,
            'email': self.email,
            'company_id': str(self.company_id),  # Convert UUID to string
            'role': self.role,
            'permission': self.permission,
            # Exclude 'pass_hash' for security reasons
            'is_active': self.is_active,
            'salary': str(self.salary) if self.salary else None,  # Handle potential None values
            'work_capacity': str(self.work_capacity) if self.work_capacity else None
        }