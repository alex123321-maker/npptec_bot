from enum import Enum
from sqlalchemy.orm import relationship

from ..base import Base

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, Enum as SqlEnum


class Statuses(Enum):
    active = 1
    not_authorized = 2
    banned = 3

class Users(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True, unique=True, autoincrement=False)
    status = Column(SqlEnum(Statuses), default=Statuses.not_authorized)

    def __init__(self, user_id, status=Statuses.not_authorized):
        self.user_id = user_id
        self.status = status


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    office_number = Column(String)
    office_phone = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))

    department = relationship("Department", back_populates="employees")

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    employees = relationship("Employee", back_populates="department")