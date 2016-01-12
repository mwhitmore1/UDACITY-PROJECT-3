from db_setup import Base, User, Posts, Pictures, Connections

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from flask import Flask, request, render_template, redirect, jsonify, url_for


app = Flask(__name__)

engine = create_engine('sqlite:///ninja.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/profile/<int:user_id>/')
def showProfile(user_id):
    print user_id
    user = session.query(User).filter_by(id=user_id).one()
    posts = session.query(Posts).filter_by(user_id=user_id)
    pictures = session.query(Pictures).filter_by(user_id=user_id)
    return render_template('profile.html',
                           user=user,
                           posts=posts,
                           pictures=pictures)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)