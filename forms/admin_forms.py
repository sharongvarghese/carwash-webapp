# forms/admin_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Login")


class ServiceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[Optional()])
    price = FloatField("Price", validators=[Optional()])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Add Service")


class PackageForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    details = TextAreaField("Details", validators=[Optional()])
    price = FloatField("Price", validators=[Optional()])
    discount_price = FloatField("Discount Price", validators=[Optional()])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Add Package")
