from sqlalchemy import Boolean, Column, String, Uuid, TEXT, VARCHAR

from database import Base

__all__ = [
    'UsersModel'
    ]

class UsersModel(Base):
    __tablename__ = 'users'

    id = Column(Uuid, primary_key=True)
    first_name = Column(TEXT, nullable=False)
    last_name = Column(TEXT, nullable=False)
    patronymic = Column(TEXT, nullable=True)
    phone_number = Column(VARCHAR(length=17), nullable=False, unique=True)
    email = Column(VARCHAR(length=40), nullable=True, unique=True)
    birth_date = Column(String, nullable=False) #Date
    hash_pass = Column(String, nullable=False)

    created_at = Column(String, nullable=False) #TimeStamp
    created_by = Column(Uuid, nullable=False)

    updated_by = Column(Uuid, nullable=False)
    updated_at = Column(String, nullable=False) #TimeStamp

    is_deleted = Column(Boolean, nullable=False, default=False)