# forms/public_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Regexp, Optional


class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField("Phone", validators=[Length(max=20)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=5)])
    submit = SubmitField("Send Message")


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


# ===============================
# NEW: REVIEW FORM
# ===============================
class ReviewForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[
            DataRequired(message="Name is required"),
            Length(min=2, max=100, message="Name must be between 2 and 100 characters")
        ]
    )
    
    display_name = StringField(
        'Display Name (Optional)',
        validators=[
            Optional(),
            Length(max=100, message="Display name must be less than 100 characters")
        ]
    )
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message="Email is required"),
            Email(message="Please enter a valid email address")
        ]
    )
    
    phone = StringField(
        'Phone',
        validators=[
            DataRequired(message="Phone number is required"),
            Length(min=10, max=20, message="Please enter a valid phone number")
        ]
    )
    
    review_text = TextAreaField(
        'Review',
        validators=[
            DataRequired(message="Review text is required"),
            Length(min=10, max=1000, message="Review must be between 10 and 1000 characters")
        ]
    )
    
    rating = SelectField(
        'Rating',
        choices=[
            ('5', '5 Stars - Excellent'),
            ('4', '4 Stars - Very Good'),
            ('3', '3 Stars - Good'),
            ('2', '2 Stars - Fair'),
            ('1', '1 Star - Poor')
        ],
        validators=[DataRequired(message="Please select a rating")],
        coerce=int
    )
    
    submit = SubmitField("Submit Review")