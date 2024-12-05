# This file contains form classes for registration, login, and other input methods.
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length

class BeneficiaryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100)])
    career_interests = StringField('Career Interests', validators=[InputRequired(), Length(min=3, max=200)])
    submit = SubmitField('Register')

class FacilitatorForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=100)])
    expertise = StringField('Expertise', validators=[InputRequired(), Length(min=3, max=200)])
    submit = SubmitField('Register')
