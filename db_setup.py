# -*- coding: utf-8 -*-
import os
import sys
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy import DateTime, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)
    profile_pic = Column(String, default='default_ninja.png')
    description = Column(String)


class Pictures(Base):
    __tablename__ = 'pictures'

    id = Column(Integer, primary_key=True)
    location = Column(String)
    description = Column(String)
    post_time = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    u_id = relationship(Users)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'location': self.location,
            'description': self.description,
            'post_time': self.post_time,
            'user_id': self.user_id
        }


class Posts(Base):
    __tablename__ = 'posts'

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    description = Column(String)
    post_time = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    u_id = relationship('Users', foreign_keys=[user_id])
    poster = Column(Integer, ForeignKey('users.id'))
    p_id = relationship('Users', foreign_keys=[poster])

    @property
    def serialize(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'description': self.description,
            'post_time': self.post_time,
            'user_id': self.user_id,
            'poster': self.poster
        }


class Connections(Base):
    __tablename__ = 'connections'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    u_id = relationship('Users', foreign_keys=[user_id])
    connected_to = Column(Integer, ForeignKey('users.id'))
    c_to = relationship('Users', foreign_keys=[connected_to])
    connected = Column(Boolean, default=False)


engine = create_engine('postgresql://vagrant@localhost/ninja')
# Bind all tables to the engine.
Base.metadata.create_all(engine)