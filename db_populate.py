from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_setup import Base, User, Posts, Pictures, Connections

engine = create_engine('sqlite:///ninja.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

newUser = User(email='ninja@ninja.com', profile_pic='url will go here')
session.add(newUser)
session.commit()

#print out databases
users = session.query(User).all()
for user in users:
    print user.id, user.email, user.profile_pic