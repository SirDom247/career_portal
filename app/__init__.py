from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_security import Security

# Initialize the Flask application and extensions
app = Flask(__name__)
app.config.from_object('app.config.Config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)
security = Security(app)

from app import routes, models
