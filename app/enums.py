from enum import IntEnum,Enum


class Roles(IntEnum):
    USER = 1
    PROVIDER = 2

class RequestStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    declined = "declined"