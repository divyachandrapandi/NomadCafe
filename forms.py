from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, URL, Email
from flask_ckeditor import CKEditorField




class AddCafeForm(FlaskForm):
    name = StringField("Cafe Name", validators=[DataRequired()])
    map_url = StringField("Map Link", validators=[DataRequired(), URL()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    location = StringField("Location", validators=[DataRequired()])
    has_sockets = BooleanField('Socket availability', default='checked')
    has_toilet = BooleanField('Toilet Facility', default='checked')
    has_wifi = BooleanField('Wifi Service', default='checked')
    can_take_calls = BooleanField('Does Permit to take calls', default='checked')
    seats = StringField("Number of seats in digits")
    coffee_price= StringField("Coffee Price in Pounds")
    submit = SubmitField("submit")

class RegisterForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email= StringField("Email Address", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit =SubmitField("Register")


class LoginForm(FlaskForm):
    email= StringField("Email Address", validators=[DataRequired(),Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit =SubmitField("Login")



















