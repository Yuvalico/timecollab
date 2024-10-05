from enum import IntEnum

class E_PERMISSIONS(IntEnum):
    net_admin = 0
    employer = 1
    employee = 2

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
            if member.value == value:
                return member
        return None  # Or raise an exception if you want to handle invalid values strictly
        
    # Permission maps
