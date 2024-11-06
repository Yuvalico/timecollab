from dataclasses import dataclass


@dataclass
class Company:
    company_id: str
    company_name: str
    is_active: bool
    users: list = None
    
    def to_dict(self):
        return {
            'company_id': str(self.company_id),  # Convert UUID to string
            'company_name': self.company_name,
            'is_active': self.is_active
        }
    def to_model(self):
        from models import CompanyModel
        return CompanyModel(
            company_id = self.company_id if self.company_id else None,  # Convert UUID to string
            company_name = self.company_name,
            is_active = self.is_active
        )