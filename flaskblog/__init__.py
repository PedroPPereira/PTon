import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy #for database use
from flask_bcrypt import Bcrypt #for user authentication porpuses
from flask_login import LoginManager #to manage login requests
from flask_mail import Mail
#inicializes web components necessary for the site

app = Flask(__name__)
app.config['SECRET_KEY'] = '2413b11315f1a45fcdd5cc3e6a487b7d' #necessery for user input
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' #database inicialization
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info' #for bootstrap information alert
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

from flaskblog import routes
