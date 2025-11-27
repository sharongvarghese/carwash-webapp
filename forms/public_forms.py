# forms/public_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, Optional


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Optional(), Length(max=20)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Send Message")


class BookingForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    service_id = SelectField("Service", coerce=int, validators=[Optional()])
    date = StringField("Date", validators=[DataRequired(), Length(max=20)])  # dd/mm/yyyy
    time = StringField("Time", validators=[DataRequired(), Length(max=20)])  # 10:30 AM
    submit = SubmitField("Book Slot")
