import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Input = declarative_base()

class User(Input):
    __tablename__ = 'User'

    id = Column(Integer, autoincrement = True)
    user_name = Column(String(250), nullable = False, primary_key = True)
    password = Column(String(250), nullable = False)

class Student(Input):
    __tablename__ = 'Student'

    regdNo = Column(String(250), ForeignKey('User.user_name'), nullable = False, primary_key = True)
    firstName = Column(String(250), nullable = False)
    lastName = Column(String(250), nullable = False)
    email = Column(String(250))
    phone = Column(Integer)
    year = Column(Integer, nullable = False,)
    branch = Column(String(250), nullable = False)
    address = Column(String(250))
    user = relationship(User)

class swim_Details(Input):
    __tablename__ = 'swim_Details'

    period = Column(Integer, primary_key = True, nullable=False)
    price = Column(Integer,nullable=False)

class swim_Requests(Input):
    __tablename__ = 'swim_Requests'

    id = Column(Integer, primary_key = True)
    userName = Column(String(250), ForeignKey('User.user_name'), nullable = False)
    period = Column(String(250), nullable = False)
    price = Column(String(250), nullable = False)
    user = relationship(User)

class image(Input):
    __tablename__ = 'image'

    id=Column(Integer, primary_key = True)
    logo = Column(LargeBinary, nullable=False)
    title = Column(String(250), nullable = False)

class Driving(Input):
    __tablename__ = 'Driving'

    id = Column(Integer, primary_key = True)
    userName = Column(String(250), ForeignKey('User.user_name'), nullable=False, unique=True)
    status = Column(Integer, default=0)
    user = relationship(User)


engine = create_engine('sqlite:///onlineRegd.db')
Input.metadata.create_all(engine)
