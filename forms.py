from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, validators, ValidationError
from wtforms.validators import InputRequired, Regexp, Length, EqualTo, Optional
#from app import User

#Login Form 
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(1, 64)])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_user = BooleanField("Keep me logged in!")
    submit = SubmitField("Log In")

#Sign up Form
class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Length(1, 64)])
    username = StringField("Username", validators=[InputRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0, 'Usernames must have only letters, numbers, dots or underscores.')])
    password2 = PasswordField("Confirm Password", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired(), EqualTo('password2', message="Passwords must match!")])
    register = SubmitField("Register")

#    def validate_email(self, field):
#       if User.query.filter_by(email=field.data).first():
#           raise ValidationError("Email already registered.")
#   def validate_username(self, field):
#       if User.query.filter_by(username=field.data).first():
#           raise ValidationError("Username already in use.")
#   Not working for some reason ^^

#Edit Profile Form
class EditProfileForm(FlaskForm):
    edit_username = StringField("Edit Username:", validators=[Optional(), Length(1, 64)])
    original_password = PasswordField("Enter Original Password:", validators=[Optional(), Length(1, 64), EqualTo("repeat_original_password", message="Old passwords must match!")])
    repeat_original_password = PasswordField("Re-enter Original Password:", validators=[Optional(), Length(1,64)])
    new_password = PasswordField("Enter New Password:", validators=[Optional(), Length(1, 64), EqualTo("repeat_new_password", message="New passwords must match!")])
    repeat_new_password = PasswordField("Re-enter New Password:", validators=[Optional(), Length(1, 64)])
    edit_email = StringField("Edit Email:", validators=[Optional(), Length(1, 64)])
    submit_button = SubmitField(" Submit Edits ")