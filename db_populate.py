from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time

from db_setup import Base, User, Posts, Pictures, Connections


engine = create_engine('sqlite:///ninja.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

newUser = User(email='ninja@ninja.com',
               profile_pic='url will go here')
session.add(newUser)
session.commit()

newPost = Posts(post_time=time.ctime(),
                subject='This is the subject',
                description='This is the description')
session.add(newPost)
session.commit()

#print out databases
users = session.query(User).all()
for user in users:
    print 'id: ',user.id
    print 'email: ',user.email
    print 'pic: ',user.profile_pic
    print ''

posts = session.query(Posts).all()
for post in posts:
    print 'post id: 'post.id
    print 'post time: ', post.post_time
    print 'post subject: ', post.subject
    print 'post description: ', post.description
    print 'poster: ', post.user_id
    print ''