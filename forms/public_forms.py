from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Length(max=20)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Send Message")


from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp


class BookingForm(FlaskForm):
    full_name = StringField("Full Name", validators=[
        DataRequired(),
        Length(min=2, max=120)
    ])

    phone = StringField("Phone Number", validators=[
        DataRequired(),
        Regexp(r'^[0-9]{10}$', message="Phone number must be 10 digits")
    ])

    email = StringField("Email", validators=[
        DataRequired(),
        Email()
    ])

    # SERVICE MUST BE SELECTED
    service_id = SelectField(
        "Service",
        coerce=int,
        validators=[DataRequired(message="Please select a service")]
    )

    date = StringField("Date", validators=[DataRequired()])
    time = StringField("Time", validators=[DataRequired()])

    submit = SubmitField("Book Slot")

    # FIXED VALIDATION (supports both 0 and "")
    def validate_service_id(self, field):
        if not field.data or field.data == 0:
            raise ValidationError("Please select a service")

