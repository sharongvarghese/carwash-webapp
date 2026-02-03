# forms/admin_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from flask_wtf.file import FileAllowed, FileField, FileRequired

class AdminLoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=100)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=4)])
    submit = SubmitField("Login")


class ServiceForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=120)])
    price = FloatField("Price", validators=[DataRequired()])
    discount_price = FloatField("Discount Price", validators=[Optional()])
    image = FileField("Image", validators=[FileAllowed(['jpg', 'jpeg', 'png', 'webp'], "Images only!")])
    description = TextAreaField("Description", validators=[Optional()])
    submit = SubmitField("Add Service")



class PackageForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired(), Length(max=120)])
    included_uses = IntegerField("Total Uses",validators=[DataRequired(), NumberRange(min=1)])
    validity_days = IntegerField( "Validity (Days)",validators=[DataRequired(), NumberRange(min=1)])
    price = FloatField("Price",validators=[DataRequired()])
    discount_price = FloatField("Discount Price",validators=[Optional()])
    badge = StringField("Badge",validators=[Optional(), Length(max=50)])
    details = TextAreaField("Details",validators=[Optional()])
    is_active = BooleanField("Is Active")
    image = FileField("Image",validators=[Optional(),
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")])
    submit = SubmitField("Save Package")



class GalleryUploadForm(FlaskForm):
    before_image = FileField(
        "Before Image",
        validators=[
            DataRequired(),
            FileAllowed(["png", "jpg", "jpeg", "webp"], "Images only!")
        ]
    )

    after_image = FileField(
        "After Image",
        validators=[
            DataRequired(),
            FileAllowed(["png", "jpg", "jpeg", "webp"], "Images only!")
        ]
    )

    caption = StringField("Caption", validators=[Optional()])

    submit = SubmitField("Upload")


class StockForm(FlaskForm):
    """Form for adding/editing stock items"""
    
    item_name = StringField('Item Name', validators=[DataRequired()], 
                           render_kw={"placeholder": "e.g., Car Shampoo"})
    
    category = SelectField('Category', 
                          choices=[
                              ('Chemicals', 'Chemicals'),
                              ('Shampoos', 'Shampoos'),
                              ('Wax', 'Wax'),
                              ('Polish', 'Polish'),
                              ('Towels', 'Towels'),
                              ('Brushes', 'Brushes'),
                              ('Other', 'Other')
                          ],
                          validators=[DataRequired()])
    
    quantity = FloatField('Quantity', 
                         validators=[DataRequired(), NumberRange(min=0)],
                         render_kw={"placeholder": "0.00"})
    
    unit = SelectField('Unit', 
                      choices=[
                          ('ltr', 'Liters (ltr)'),
                          ('ml', 'Milliliters (ml)'),
                          ('kg', 'Kilograms (kg)'),
                          ('g', 'Grams (g)'),
                          ('pcs', 'Pieces (pcs)'),
                          ('bottles', 'Bottles'),
                          ('cans', 'Cans'),
                          ('boxes', 'Boxes')
                      ],
                      validators=[DataRequired()])
    
    notes = TextAreaField('Notes (Optional)', 
                         render_kw={"placeholder": "Additional notes about this item..."})
    
    submit = SubmitField('Save Item')


class StockTransactionForm(FlaskForm):
    """Form for stock transactions (add/reduce/adjust)"""
    
    transaction_type = SelectField('Action',
                                  choices=[
                                      ('add', 'Add Stock'),
                                      ('reduce', 'Reduce Stock'),
                                      ('adjust', 'Adjust Stock')
                                  ],
                                  validators=[DataRequired()])
    
    quantity = FloatField('Quantity',
                         validators=[DataRequired(), NumberRange(min=0.01)],
                         render_kw={"placeholder": "0.00"})
    
    reason = StringField('Reason',
                        validators=[DataRequired()],
                        render_kw={"placeholder": "e.g., Used for service, Restocked"})
    
    submit = SubmitField('Update Stock')
