from classes.RC import RC
from classes.RC import E_RC
from enum import IntEnum

class E_PERMISSIONS(IntEnum):
    net_admin = 0
    employer = 1
    employee = 2
    
    def __call__(self, value):
        try:
            return E_PERMISSIONS(int(value))  # Try converting to int
        except ValueError:
            return "Invalid Permission"

    def to_str(self):
        """
        Returns a string representation of the enum member.
        """
        try:
            return self.name 
        
        except Exception as e:
            return "unknown"
        
    @staticmethod
    def to_enum(value):
        """
        Converts a value to its corresponding enum member.

        Args:
            value: The value to convert.

        Returns:
            MyEnum or None: The enum member with the matching value, or None if not found.
        """
        for member in E_PERMISSIONS:
            if member.value == int(value):
                return member
        return RC(E_RC.RC_INVALID_INPUT, f"Invalid permission level {value}")
    
class Permission():
    def __init__(self, permission: E_PERMISSIONS):
            self.permission = permission
    
    def is_net_admin(self) -> bool:
        return self.permission == E_PERMISSIONS.net_admin

    def is_employer(self) -> bool:
        return self.permission == E_PERMISSIONS.employer

    def is_employee(self) -> bool:
        return self.permission == E_PERMISSIONS.employee
    
    