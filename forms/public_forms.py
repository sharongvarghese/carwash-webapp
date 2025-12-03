from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Length(max=20)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Send Message")


class BookingForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    phone = StringField("Phone Number", validators=[DataRequired(), Length(max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])

    # SERVICE MUST BE SELECTED (NO EMPTY VALUE ALLOWED)
    service_id = SelectField("Service", coerce=int, validators=[DataRequired()])

    # date/time come from JS → hidden inputs
    date = StringField("Date", validators=[DataRequired()])
    time = StringField("Time", validators=[DataRequired()])

    submit = SubmitField("Book Slot")

    # custom validation → 0 means "Select Service"
    def validate_service_id(self, field):
        if field.data == 0:
            raise ValidationError("Please select a service")
