from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import time

from db_setup import Base, User, Posts, Pictures, Connections


engine = create_engine('sqlite:///ninja.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

newUser = User(email='ninja@ninja.com',
               profile_pic='ninja.png',
               username='ninja',
               description='''This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.  ''')
session.add(newUser)
session.commit()

newUser = User(email='ninja@ninja.com',
               profile_pic='redninja2.png',
               username='redninja',
               description='''This is a description text block.
               This is a dfdescriptreiafdon text block.
               This aifes a description textvf block.
               This idfas a desdcriptrion text block.
               Thisdfaa is a descddarrifption text block.
               This weris a descripdwftion text block.
               Thisr is a description text block.  ''')
session.add(newUser)
session.commit()


newUser = User(username='pinkninja'
               )
session.add(newUser)
session.commit()

newConnection = Connections(user_id=1, connected_to=2)
session.add(newConnection)
newConnection2 = Connections(user_id=2, connected_to=1)
session.add(newConnection2)
newConnection3 = Connections(user_id=1, connected_to=3)
session.add(newConnection3)
newConnection4 = Connections(user_id=3, connected_to=1)
session.add(newConnection4)
session.commit()


newPicture = Pictures(location='ninja.png',
                      user_id=1)
session.add(newPicture)

session.commit()

newPost = Posts(post_time=time.ctime(),
                user_id=1,
                subject='This is the subject',
                description='''This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.
               This is a description text block.  ''')
session.add(newPost)
session.commit()

#print out databases
users = session.query(User).all()
for user in users:
    print 'id: ',user.id
    print 'username: ', user.username
    print 'description: ', user.description
    print 'email: ',user.email
    print 'pic: ',user.profile_pic
    print ''

pictures = session.query(Pictures).all()
for picture in pictures:
    print "picture id: ", picture.id
    print "picture location: ", picture.location
    print "poster id: ", picture.user_id


posts = session.query(Posts).all()
for post in posts:
    print 'post id: ', post.id
    print 'post time: ', post.post_time
    print 'post subject: ', post.subject
    print 'post description: ', post.description
    print 'poster: ', post.user_id
    print ''