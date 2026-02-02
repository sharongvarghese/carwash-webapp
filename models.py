# models.py
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db, login_manager


class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=True)
    discount_price = db.Column(db.Float, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    bookings = db.relationship("Booking", backref="service", lazy=True)


class Package(db.Model):
    __tablename__ = "packages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    total_uses = db.Column(db.Integer, nullable=False, default=0)      
    validity_days = db.Column(db.Integer, nullable=False, default=30)
    price = db.Column(db.Float, nullable=False)
    discount_price = db.Column(db.Float, nullable=True)
    details = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    badge = db.Column(db.String(50), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

from extensions import db
from datetime import datetime, date

class PackagePurchase(db.Model):
    __tablename__ = "package_purchases"

    id = db.Column(db.Integer, primary_key=True)

    # Customer info
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)

    # Package relation
    package_id = db.Column(db.Integer, db.ForeignKey("packages.id"), nullable=False)
    package = db.relationship("Package", backref="purchases")

    # Tracking
    total_uses = db.Column(db.Integer, nullable=False)
    remaining_uses = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)

    status = db.Column(db.String(20), default="Active")  # Active / Expired / Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PackagePurchase {self.id} - {self.full_name}>'
    
    @property
    def is_expired(self):
        """Check if package has expired"""
        return date.today() > self.expiry_date
    
    @property
    def is_completed(self):
        """Check if all uses are consumed"""
        return self.remaining_uses <= 0
    
    @property
    def days_remaining(self):
        """Calculate days remaining until expiry"""
        delta = self.expiry_date - date.today()
        return max(0, delta.days)
    
    @property
    def auto_status(self):
        """Automatically determine status"""
        if self.remaining_uses <= 0:
            return "Completed"
        elif self.is_expired:
            return "Expired"
        else:
            return "Active"


class Booking(db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=True)
    date = db.Column(db.String(20), nullable=False)   # dd/mm/yyyy
    time = db.Column(db.String(20), nullable=False)   # e.g. 10:30 AM
    status = db.Column(db.String(20), default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50))  # booking / package_booking / contact / review
    message = db.Column(db.String(255))
    reference_id = db.Column(db.Integer, nullable=True)  
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    __tablename__ = "contact_messages"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GalleryImage(db.Model):
    __tablename__ = "gallery_images"

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=True)
    before_image = db.Column(db.String(255), nullable=False)
    after_image = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255), nullable=True)
    service = db.relationship("Service")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Review(db.Model):
    __tablename__ = "reviews"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    display_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_approved = db.Column(db.Boolean, default=True)  # Auto-approve, admin can delete
    
    def __repr__(self):
        return f'<Review {self.id} - {self.get_display_name()}>'
    
    def get_display_name(self):
        """Returns display_name if available, otherwise returns name"""
        return self.display_name if self.display_name else self.name
    
    def get_star_display(self):
        """Returns filled and empty stars for display"""
        filled = '★' * self.rating
        empty = '☆' * (5 - self.rating)
        return filled + empty 

class Stock(db.Model):
    __tablename__ = "stocks"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # Chemicals, Shampoos, Wax, Polish, Towels, etc.
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20))  # kg, ltr, pcs, bottles, etc.
    notes = db.Column(db.Text)  # Optional notes about the item
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def stock_status(self):
        """Get stock status"""
        if self.quantity == 0:
            return "Out of Stock"
        elif self.quantity <= 5:  # Low stock if 5 or less units
            return "Low Stock"
        else:
            return "In Stock"
    
    @property
    def is_low_stock(self):
        """Check if stock is low (5 or less units)"""
        return 0 < self.quantity <= 5
    
    @property
    def is_out_of_stock(self):
        """Check if completely out of stock"""
        return self.quantity == 0


class StockTransaction(db.Model):
    __tablename__ = "stock_transactions"

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'), nullable=False)
    transaction_type = db.Column(db.String(20))  # 'add', 'reduce', 'adjust'
    quantity = db.Column(db.Float)
    previous_quantity = db.Column(db.Float)
    new_quantity = db.Column(db.Float)
    reason = db.Column(db.String(255))  # "Used for service", "Restocked", "Inventory adjustment", etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    stock = db.relationship('Stock', backref=db.backref('transactions', lazy='dynamic', order_by='StockTransaction.created_at.desc()'))

    def __repr__(self):
        return f'<StockTransaction {self.transaction_type} - {self.quantity}>'
