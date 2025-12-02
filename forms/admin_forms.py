# forms/admin_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileAllowed, FileField

class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Login")


class ServiceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    price = FloatField("Price", validators=[DataRequired()])
    image = FileField("Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images only!")])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Add Service")



class PackageForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=120)])
    details = TextAreaField("Details", validators=[Optional()])
    price = FloatField("Price", validators=[Optional()])
    discount_price = FloatField("Discount Price", validators=[Optional()])
    image_url = StringField("Image URL", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Add Package")



class GalleryUploadForm(FlaskForm):
    image = FileField("Upload Image", validators=[
        DataRequired(),
        FileAllowed(["png", "jpg", "jpeg", "webp"], "Images only!")
    ])
    caption = StringField("Caption", validators=[Optional()])
    submit = SubmitField("Upload")
