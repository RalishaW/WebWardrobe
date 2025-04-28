from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo
from flask_wtf.file import FileField, FileAllowed
from models import User

# ----------------------
# Form Models using Flask
# ----------------------
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()]
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# RegisterForm in Flask to improve security
class RegisterForm(FlaskForm):
    username = StringField('User', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Retype password do not match. Please try again')])
    email

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

# class ResetPasswordForm(FlaskForm):
    

class ProfilePicture(FlaskForm):
    profile_picture = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'jpeg', 'png']), 'Images type: jpg, jpeg, png only'])
