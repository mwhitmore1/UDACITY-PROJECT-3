import os

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


@app.route('/profile/<int:user_id>/', methods=['GET', 'POST'])
def showProfile(user_id):
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('showProfile', user_id=user_id))
    else:
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