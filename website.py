import os

import time

from db_setup import Base, User, Posts, Pictures, Connections

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from werkzeug import secure_filename

from flask import Flask, request, render_template, redirect, jsonify, url_for


UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jqeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///ninja.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1]\
    in ALLOWED_EXTENSIONS


@app.route('/profile/<int:user_id>/pic/<int:picture_id>', methods=['GET', 'POST'])
def viewPic(user_id, picture_id):
    picture = session.query(Pictures).filter_by(id=picture_id).one()
    return render_template('viewpic.html', user_id=user_id, picture=picture)


@app.route('/profile/<int:user_id>/add_pic/<int:picture_id>', methods=['GET', 'POST'])
def addPic(user_id, picture_id):
    picture = session.query(Pictures).filter_by(id=picture_id).one()
    if request.method == 'POST':
        picDescr = request.form['picdes']
        picture.description = picDescr
        return redirect(url_for('showProfile', user_id=user_id))
    else:

        return render_template('addpic.html', user_id=user_id, picture=picture)


@app.route('/profile/<int:user_id>/', methods=['GET', 'POST'])
def showProfile(user_id):
    if request.method == 'POST':
        if request.form['newpost']:
            newPost = Posts(user_id=user_id,
                            description=request.form['newpost'],
                            post_time=time.ctime())
            session.add(newPost)
            session.commit()
            return redirect(url_for('showProfile', user_id=user_id))
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            newPicture = Pictures(location=filename,
                                  post_time=time.ctime(),
                                  user_id=user_id)
            session.add(newPicture)
            session.commit()
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('addPic', user_id=user_id, picture_id=newPicture.id))
    else:
        user = session.query(User).filter_by(id=user_id).one()
        posts = session.query(Posts).filter_by(user_id=user_id)
        pictures = session.query(Pictures).filter_by(user_id=user_id)
        connections = session.query(Connections, User).filter(Connections.user_id==user_id, User.id==Connections.connected_to)
        return render_template('profile.html',
                               user=user,
                               posts=posts,
                               connections=connections,
                               pictures=pictures)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)