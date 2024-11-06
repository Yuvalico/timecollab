class RC:
    """
    Return Code class to encapsulate return codes and their descriptions.
    """

    def __init__(self, code: int, description: str):
        self.code = code
        self.description = description

    def __str__(self):
        return f"{self.description}"

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "code": self.code,
            "description": self.description,
        }