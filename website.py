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

# Get client ID from client_secrets file.
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']\
    ['client_id']
APPLICATION_NAME = 'The Social Ninja'


def allowed_file(filename):
    # will return true if the filename contains a period and has an extension
    # to the right of the period that is in the ALLOWED_EXTENSIONS list.
    return '.' in filename and filename.rsplit('.', 1)[1]\
    in ALLOWED_EXTENSIONS


@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
        for i in range(32))
    print 'State created:', state
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/logout/')
def logout():
    return render_template('logout.html')


@app.route('/gconnect', methods = ['POST'])
def gconnect():
    # Check if the stat token in the user request is the same as the state code
    # on the server.
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data.decode('utf-8')
    print request.data.decode('utf-8')
    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        print 'Flow object created from client_secrets file'
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
        print 'Flow object exchanged for for credentials'
    except:
        response = make_response(
            json.dumps('Failed to update the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    # Send a request to Google with the access token.
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps\
            ('The google server returned an error.'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    print 'gplus_id obtained from creentials object:', gplus_id
    # Check if gplus_id from user is the same as from google.
    if gplus_id != result['user_id']:
        response = make_response(json.dumps(
            "Tokens's user id doesn't match given user id."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check if client id is the same from Google as on host server.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Tokens's client id doesn't match apps."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store credentials for future use.
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    login_session['credentials'] = access_token
    login_session['gplus_id'] = gplus_id
    # Check to see if user is already logged in.
    if stored_credentials and stored_gplus_id == gplus_id:
        try:
            user = session.query(User).filter_by(email=login_session['email']).one()
            # Raise an exception if user has no name to avoid users returning
            # to the new account page once they have created an account.
            if user.username == '':
                raise
            # Send user to their profile page if they are already logged in.
            response = make_response(json.dumps(
                {"message": "Current user is already logged in.",
                 'user': login_session['id']}), 200)
            response.headers['Content-Type'] = 'application/json'
            return response
        except:
            pass
    # Get user info.
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['email'] = data['email']
    # Check if user has an existing account.
    try:
        user = session.query(User).filter_by(email=login_session['email']).one()
        # Delete user if no username is specified to avoid visits to the create
        # account page after user has already created an account.
        if user.username == '':
            session.delete(user)
            session.commit()
            raise
        login_session['id'] = user.id
        flash('You are logged in as %s.' % user.username)
        # Send the user id back to the client to allow them to view the profile.
        response = make_response(json.dumps(
            {'user': user.id}), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    except:
        # Send response back to client that will direct the user to create an
        # account.
        response = make_response(json.dumps(
            {'user': None}), 200)
        response.headers['Content-Type'] = 'application/json'
        user = User(username='', email=login_session['email'])
        session.add(user)
        session.commit()
        # Set login session variables.
        login_session['id'] = user.id
        login_session['username'] = user.username
        return response


@app.route('/gdisconnect')
def gdisconnect():
    # Send to login if user is not logged in.
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    access_token = login_session['credentials']
    # Send the client an error if the user is not logged in.
    if access_token is None:
        response = make_response(json.dumps('User not logged in.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    # Send the access token to the Google server to log out the user.
    result = json.loads(h.request(url, 'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps('Log out failed.'), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Delete all login session objects
    del login_session['credentials']
    del login_session['email']
    del login_session['gplus_id']
    del login_session['id']
    del login_session['username']
    flash('Logout Successful!')
    return redirect(url_for('logout'))


@app.route('/join', methods = ['GET', 'POST'])
def newAccount():
    # Send to login if user is not logged in.
    if login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    user = session.query(User).filter_by(id=login_session['id']).one()
    if request.method == 'POST':
        # Update user''s username.
        user.username=request.form['newname']
        login_session['username'] = user.username
        return redirect(url_for('showProfile', user_id=user.id))
    else:
        return render_template('newaccount.html')


@app.route('/ninjas')
def ninjas():
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    ninjas = session.query(User).all()
    return render_template('ninjas.html',
                           ninjas=ninjas,
                           login=login_session['id'])


@app.route('/profile/<int:user_id>/pic/<int:picture_id>',
           methods=['GET', 'POST'])
def viewPic(user_id, picture_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    picture = session.query(Pictures).filter_by(id=picture_id).one()
    user = session.query(User).filter_by(id=user_id).one()
    if request.method == 'POST':
        # Edit picture description.
        if request.form.get('editdescription'):
            picture.description = request.form['editdescription']
            return redirect(url_for('viewPic',
                                    user_id=user_id,
                                    picture_id=picture_id))
        # Delete picture.
        if request.form.get('delyes'):
            session.delete(picture)
            session.commit()
            flash("Picture deleted.")
            return redirect(url_for('showProfile', user_id=user_id))
        # Set picture as profile picture.
        if request.form.get('propic'):
            flash('Profile picture changed')
            user.profile_pic = picture.location
            return redirect(url_for('showProfile', user_id=user_id))
    return render_template('viewpic.html',
                           user=user,
                           picture=picture,
                           login=login_session['id'])


@app.route('/profile/<int:user_id>/add_pic/<int:picture_id>',
           methods=['GET', 'POST'])
def addPic(user_id, picture_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    # Send any user other thant the owner of the picture back to the owner's
    # profile page.
    if login_session['id'] != user_id:
        return redirect(url_for('showProfile', user_id=user_id))
    picture = session.query(Pictures).filter_by(id=picture_id).one()
    user = session.query(User).filter_by(id=user_id).one()
    if request.method == 'POST':
        # Delte picture if user presses 'cancel'
        if request.form.get('cancel'):
            session.delete(picture)
            session.commit()
        # Update the pictures description.
        picDescr = request.form['picdes']
        picture.description = picDescr
        flash("Picture added/edited.")
        return redirect(url_for('showProfile', user_id=user_id))
    else:
        return render_template('addpic.html',
                               user=user,
                               picture=picture,
                               login=login_session['id'])


@app.route('/profile/<int:user_id>/connections/')
def viewConnections(user_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    user = session.query(User).filter_by(id=user_id).one()
    connections = session.query(Connections, User)\
        .filter(Connections.user_id==user_id,
                User.id==Connections.connected_to).all()
    return render_template('viewcon.html',
                           user=user,
                           connections=connections,
                           login=login_session['id'])


@app.route('/profile/<int:user_id>/requests/', methods=['GET', 'POST'])
def viewRequests(user_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    # Send any user other thant the owner of the picture back to the owner's
    # profile page.
    if login_session['id'] != user_id:
        return redirect(url_for('showProfile', user_id=user_id))
    user = session.query(User).filter_by(id=user_id).one()
    # List all users who have sent user a friend request.
    connections = session.query(Connections, User)\
        .filter(Connections.user_id == User.id,
                Connections.connected_to == user_id,
                Connections.connected==False).all()
    if request.method == 'POST':
        # Accept a friend request.
        if request.form.get('accept'):
            acceptIndex = int(request.form['index'])
            accCon = session.query(Connections).filter_by(id=acceptIndex).one()
            accCon.connected = True
            newCon = Connections(user_id=user_id,
                                 connected_to=acceptIndex,
                                 connected=True)
            session.add(newCon)
            session.commit()
            flash("You are now friends with " + user.username)
            return redirect(url_for('viewRequests', user_id=user_id))
        # Decline a friend request
        if request.form.get('decline'):
            deleteIndex = int(request.form['index'])
            delCon = session.query(Connections).filter_by(id=deleteIndex).one()
            session.delete(delCon)
            session.commit()
            return redirect(url_for('viewRequests', user_id=user_id))
    return render_template('viewreq.html',
                           user=user,
                           connections=connections,
                           login=login_session['id'])


@app.route('/profile/<int:user_id>/', methods=['GET', 'POST'])
def showProfile(user_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    user = session.query(User).filter_by(id=user_id).one()
    if request.method == 'POST':
        # Add a new post.
        if request.form.get('newpost'):
            newPost = Posts(user_id=user_id,
                            subject=request.form['postsubject'],
                            description=request.form['newpost'],
                            post_time=time.ctime(),
                            poster=login_session.get('id'))
            print login_session.get('id')
            session.add(newPost)
            session.commit()
            flash('You have posted a message on %s\'s page.' % user.username)
            return redirect(url_for('showProfile', user_id=user_id))
        # Edit user description.
        if request.form.get('editdescription'):
            user.description = request.form['editdescription']
            flash('Your profile description has been edited.')
            return redirect(url_for('showProfile', user_id=user_id))
        # Send a friend request.
        if request.form.get('sendreq'):
            connection = Connections(user_id=login_session['id'],
                                     connected_to=user.id)
            session.add(connection)
            session.commit()
            connections = session.query(Connections)\
                .filter_by(user_id=user_id,
                           connected_to=login_session['id']).all()
            flash("You have sent a friend request to " + user.username)
            # Add the user to the friend's list if they have also sent a friend
            # request.
            if connections != []:
                connection.connected = True
                connections[0].connected = True
                flash("You are now friends with " + user.username)
            return redirect(url_for('showProfile', user_id=user_id))
        # Upload a picture file.
        if request.files.get('file'):
            file = request.files['file']
            # Check if filed is in poper format.
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                newPicture = Pictures(post_time=time.ctime(),
                                      user_id=user_id)
                session.add(newPicture)
                session.commit()
                # give file a unique name.
                filename= 'image_' + str(newPicture.id) + '_' + filename
                newPicture.location = filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                return redirect(url_for('addPic',
                                        user_id=user.id,
                                        picture_id=newPicture.id))
    else:
        posts = session.query(Posts, User)\
            .filter(Posts.user_id==user_id,
                    Posts.poster==User.id).order_by(desc(Posts.id)).all()
        pictures = session.query(Pictures).filter_by(user_id=user_id).all()
        connections = session.query(Connections, User)\
            .filter(Connections.connected==True,
                    Connections.user_id==user_id,
                    User.id==Connections.connected_to).all()
        try:
        # The followig will determine what is to be displayed where the friend
        # request button usually appears.
            c = session.query(Connections)\
                .filter_by(user_id=login_session['id'],
                           connected_to=user.id).one()
            try:
                c_to = session.query(Connections)\
                    .filter_by(user_id=user.id,
                               connected_to=login_session['id']).one()
                requestSent = 2
            except:
                requestSent = 1
        except:
            requestSent = 0
        print 'requestSent', requestSent
        for pic in pictures:
            print pic.id, pic.location
        return render_template('profile.html',
                               user=user,
                               posts=posts,
                               connections=connections,
                               pictures=pictures,
                               login=login_session['id'],
                               requestSent=requestSent)


@app.route('/profile/<int:user_id>/json_pics')
def jsonPics(user_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    pictures = session.query(Pictures).filter_by(user_id=user_id).all()
    return jsonify(Pictures=[i.serialize for i in pictures])


@app.route('/profile/<int:user_id>/json_posts')
def jsonPosts(user_id):
    if login_session.get('username') == ''\
            or login_session.get('id') is None:
        flash('You must be logged in to view content.')
        return redirect(url_for('showLogin'))
    posts = session.query(Posts).filter_by(user_id=user_id).all()
    return jsonify(Posts=[i.serialize for i in posts])


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
