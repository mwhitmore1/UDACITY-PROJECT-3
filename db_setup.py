# -*- coding: utf-8 -*-
import os
import sys
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    profil_pic = Column(String)


class Pictures(Base):

    __tablename__ = 'pictures'

    id = Column(Integer, primary_key=True)
    location = Column(String)
    description = Column(String)
    post_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    u_id = relationship(User)


class Posts(Base):

    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    description = Column(String)
    post_time = Column(DateTime)
    user_id = Column(Integer, ForeignKey('user.id'))
    u_id = relationship(User)


class Connections(Base):

    __tablename__ = 'connections'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    u_id = relationship(User)
    connected_to = Column(Integer, ForeignKey('user.id'))
    c_to = relationship(User)


engine = create_engine('sqlite:///ninja.db')
Base.metadata.create_all(engine)