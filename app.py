import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash, Blueprint, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, InputRequired, Email, Length
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from authlib.integrations.flask_client import OAuth  # For Google OAuth

# Load environment variables
load_dotenv()

# Initialize extensions
bp = Blueprint('main', __name__)
db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
oauth = OAuth()  # For OAuth2 integration

# Create Flask app
def create_app():
    app = Flask(__name__)

    # App configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}@"
        f"{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # To avoid overhead
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'your_secret_key_here'  # Default secret key fallback

    # Email configuration
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))  # Default to 587 if not set
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    Migrate(app, db)
    oauth.init_app(app)

    # Configure Google OAuth2
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={'scope': 'openid email profile'}
    )

    # Register the blueprint
    app.register_blueprint(bp)

    # Register the user_loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


# Define forms
class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=100)])
    lastname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    matric_number = StringField('Matric Number', validators=[DataRequired(), Length(max=100)])
    school = StringField('School', validators=[DataRequired(), Length(max=100)])
    department = StringField('Department', validators=[DataRequired(), Length(max=100)])
    career_interests = StringField('Career Interests', validators=[DataRequired(), Length(max=200)])
    submit = SubmitField('Register')

# Define forms
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')

# Define routes

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if the email is already registered
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address already exists!', 'danger')
            return redirect(url_for('main.register'))

        # Create a new user object with hashed password
        new_user = User(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            matric_number=form.matric_number.data,
            school=form.school.data,
            department=form.department.data,
            career_interests=form.career_interests.data
        )
        new_user.set_password(form.password.data)  # Hash the password

        # Add user to the database
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')

    return render_template('register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid email or password!', 'danger')

    return render_template('login.html', form=form)


@bp.route('/login/google')
def google_login():
    redirect_uri = url_for('main.google_auth_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/auth/callback')
def google_auth_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')

    if user_info:
        user = User.query.filter_by(email=user_info['email']).first()

        if not user:
            # Register the user if they don't exist
            user = User(
                firstname=user_info['given_name'],
                lastname=user_info['family_name'],
                email=user_info['email']
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        flash('Logged in successfully with Google!', 'success')
        return redirect(url_for('main.index'))

    flash('Authentication failed!', 'danger')
    return redirect(url_for('main.login'))


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out.', 'info')
    return redirect(url_for('main.index'))


# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True)  # Optional for OAuth users
    matric_number = db.Column(db.String(100), unique=True, nullable=True)
    school = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    career_interests = db.Column(db.String(200), nullable=True)
    
    # OAuth relationship
    oauth = db.relationship('OAuthUser', back_populates='user', uselist=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class OAuthUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)
    provider = db.Column(db.String(255), nullable=False)
    provider_id = db.Column(db.String(255), nullable=False)
    token = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    token_expires = db.Column(db.DateTime)

    user = db.relationship('User', back_populates='oauth')


# Run the app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
