class BaseModel:
    
    def __init__(self, diction: dict):
        self.__diction = diction
    
    def to_dict(self) -> dict:
        return self.__diction
