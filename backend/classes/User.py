
from cmn_utils import iso2datetime, datetime2iso
from dataclasses import dataclass
from datetime import datetime, timezone
from cmn_utils import print_exception, datetime2iso, iso2datetime
from classes.Company import Company

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
    company: Company = None
    
    
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
            'employment_start': datetime2iso(self.employment_start),
            'employment_end': datetime2iso(self.employment_end),
            'weekend_choice': self.weekend_choice
        }
        
    def to_model(self):
        from models import UserModel
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
        