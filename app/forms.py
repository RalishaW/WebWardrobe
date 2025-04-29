from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Optional, AnyOf
from flask_wtf.file import FileField, FileAllowed

# ----------------------
# Form Models using Flask
# ----------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Retype password do not match. Please try again')])
    terms = BooleanField('I agree to the Terms & Conditions', validators=[DataRequired()])
    submit = SubmitField('Sign-Up')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Password Reset Form')

class ProfilePicture(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])

class ClothingItemForm(FlaskForm):
    image = FileField('Clothing Item Image', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')])
    color = StringField('Clothing Item Color', validators=[Optional()])
    season = StringField('Season', validators=[AnyOf(['Winter', 'Summer', 'Spring', 'Autumn'], message='Season must be Winter, Summer, Spring, or Autumn')])
    

# class RemoveClothingItemForm(FlaskForm):

