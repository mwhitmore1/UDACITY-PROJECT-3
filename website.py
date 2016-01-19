import os
import time
import random
import string
import httplib2
import requests

from db_setup import Base, User, Posts, Pictures, Connections

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

from werkzeug import secure_filename

from flask import Flask, request, render_template, redirect, jsonify, \
                  url_for, flash, json, make_response

from flask import session as login_session


UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jqeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///ninja.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = 'Ninja Network'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1]\
    in ALLOWED_EXTENSIONS


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
        for i in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods = ['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except:
        response = make_response(
            json.dumps('Failed to update the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps('Error.'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if gplus_id != result['user_id']:
        response = make_response(json.dumps(
            "Tokens's user id doesn't match given user id."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Tokens's client id doesn't match apps."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    login_session['credentials'] = access_token
    login_session['gplus_id'] = gplus_id
    if stored_credentials and stored_gplus_id == gplus_id +'k':
        response = make_response(json.dumps(
            "Current user is already logged in."), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    login_session['email'] = data['email']
    try:
        user = session.query(User).filter_by(email=login_session['email']).one()
        login_session['id'] = user.id
        flash('%s has logged in.' % user.username)
        return url_for('showProfile', user_id=user.id)
    except:
        response = make_response(json.dumps(
            {'user': None}), 200)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session['credentials']
    if access_token is None:
        response = make_response(json.dumps('User not logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps('Log out failed.'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    del login_session['credentials']
    del login_session['email']
    del login_session['gplus_id']
    del login_session['id']
    flash('Logout Successful!')
    return redirect(url_for('showLogin'))


@app.route('/join', methods = ['GET', 'POST'])
def newAccount():
    if request.method == 'POST':
        newUser = User(username=request.form['newname'])
        session.add(newUser)
        session.commit()
        login_session['id'] = newUser.id
        return redirect(url_for('showProfile', user_id=newUser.id))
    else:
        return render_template('newaccount.html')


@app.route('/profile/<int:user_id>/pi/<int:picture_id>', methods=['GET', 'POST'])
def viewPic(user_id, picture_id):
    picture = session.query(Pictures).filter_by(id=picture_id).one()
    return render_template('viewpic.html', picture=picture)


@app.route('/profile/<int:user_id>/add_pic/<int:picture_id>', methods=['GET', 'POST'])
def addPic(user_id, picture_id):
    print 'addPic called.'
    picture = session.query(Pictures).filter_by(id=picture_id).one()
    user = session.query(User).filter_by(id=user_id).one()
    if request.method == 'POST':
        if request.form.get('cancel'):
            session.delete(picture)
            session.commit()
        picDescr = request.form['picdes']
        picture.description = picDescr
        return redirect(url_for('showProfile', user_id=user_id))
    else:
        return render_template('addpic.html', user=user, picture=picture)


@app.route('/profile/<int:user_id>/connections/')
def viewConnections(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    connections = session.query(Connections, User).filter(Connections.user_id==user_id, User.id==Connections.connected_to).all()
    return render_template('viewcon.html', user=user, connections=connections)

@app.route('/profile/<int:user_id>/', methods=['GET', 'POST'])
def showProfile(user_id):
    print 'show profile'
    user = session.query(User).filter_by(id=user_id).one()
    if request.method == 'POST':
        print 'end'
        if request.form.get('newpost'):
            newPost = Posts(user_id=user_id,
                            subject=request.form['postsubject'],
                            description=request.form['newpost'],
                            post_time=time.ctime(),
                            poster=login_session.get('id'))
            print login_session.get('id')
            session.add(newPost)
            session.commit()
            return redirect(url_for('showProfile', user_id=user_id))
        if request.form.get('editdescription'):
            user.description = request.form['editdescription']
            return redirect(url_for('showProfile', user_id=user_id))
        print 'picture upload'
        if request.files.get('file'):
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                newPicture = Pictures(post_time=time.ctime(),
                                      user_id=user_id)
                session.add(newPicture)
                session.commit()
                filename= 'image_' + str(newPicture.id) + '_' + filename
                newPicture.location = filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('addPic', user_id=user.id, picture_id=newPicture.id))
    else:
        posts = session.query(Posts, User).filter(Posts.user_id==user_id, Posts.poster==User.id).order_by(desc(Posts.id)).all()
        pictures = session.query(Pictures).filter_by(user_id=user_id).all()
        connections = session.query(Connections, User).filter(Connections.user_id==user_id, User.id==Connections.connected_to).all()
        #if login_session.get('id') == user_id:
        for pic in pictures:
            print pic.id, pic.location
        return render_template('profile.html',
                                   user=user,
                                   posts=posts,
                                   connections=connections,
                                   pictures=pictures)

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)