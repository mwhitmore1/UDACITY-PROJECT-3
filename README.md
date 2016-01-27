REQUIREMENTS

This readme assumes you are using a UNIX command line.  The app will be run locally on port 5000, thus it will not run properly if this port Is blocked by a firewall.  You will need to have Python 2 installed.  In order to create an account on the app, you will need to have a Gmail account.  

SETUP

To setup this app, open a UNIX command line and navigate to the directory where you downloaded this app.  Make sure that there is a file called load.bash.  type 'bash load.bash' in the command line and press 'Enter.'. This will run the database setup file, a database population file, and the file which sets up the server.  The file which populates the database, 'db_populate.py', fills the database with test data.  If you do not wish to add this data, you can type "python db_setup.py; python website.py" in lieu of "bash load.bash."

USE

Create an Account

Once you have followed the SETUP instructions the app will be running on localhost:5000.  Only the login page, 'http://localhost:5000/login' will be accessible.  Open a web browser and navigate to 'http://localhost:5000/login.'. Press the 'Sign In' button to login.  A window will appear that will prompt you to log in via your Gmail account, press 'Allow' to do so.  You will be directed to an account creation page.  Enter a username in the appropriate text box.  You will not be able to create an account without entering a user name.  You will also required to verify that you are in fact a ninja.  If You follow these steps successfully, an account will be create and you will be directed to your profile page.  

Your Profile

You may add a description to your profile by clicking the 'edit description' button.  This will cause a form to appear on the screen.  Type your desired description into the text box and press 'submit.'. The page will reload and will now display the edited description.  

To add a post follow the same steps as editing a description, except press 'Add Post' instead of 'edit description.'. This feature can be used on any other user's profile page, in addition to your own.  

You can add a picture by selecting a file with the 'browse' button on the left side of the screen and press 'Upload Picture' to upload the picture.  You will be directed to a page that will allow you to give the picture a description.  If you do not wish to upload the picture, you may press cancel, and it will be deleted from the server (but not from wherever you uploaded it from).  Otherwise, press 'submit' to save the picture.  You will be redirected to your profile and the picture should now appear under 'Pictures.'. If you click on the now uploaded picture, you will be directed to a page where you can edit the description, and/or set the picture as your profile picture.  

To view any friend requests you have received click on 'Requests' at the top of the screen.  You will be directed to the 'Friend Requests' page.  If you have been sent a friend request it will appear here.  There will be an 'accept' button and a 'decline' button under each requests.  Since the app is being run locally it is extremely unlikely friend requests will appear.  You may send friend requests of your own while on a given user's profile by pressing the 'send friend request' button located under the user's profile picture.  Given that the app is run locally, however, this may be an exercise in futility.  

To view all other users on the app, click the 'All Ninjas' button near the top of the page.  If you setup the app with the database populated, several other users will appear.  

Pressing the 'Profile' button near the top of the page will return you back to your profile.  

Finally, pressing the 'Log Out' button in the top right corner will will log you out.  
