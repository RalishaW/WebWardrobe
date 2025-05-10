from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired, InputRequired, EqualTo, Length, Email

# ----------------------
# Form Models using Flask
# ----------------------
class LoginForm(FlaskForm):
    # username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=80)])
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Retype password do not match. Please try again')])
    terms = BooleanField('I agree to the Terms & Conditions', validators=[DataRequired()])
    submit = SubmitField('Sign-Up')

class RequestResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=4)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Password must match")])
    submit = SubmitField('Reset Password')

# class RemoveClothingItemForm(FlaskForm):

