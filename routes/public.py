# routes/public.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from extensions import db, mail
from models import Service, Package, Booking, Notification, ContactMessage, GalleryImage, Review, PackagePurchase
from forms.public_forms import ContactForm, BookingForm, ReviewForm, PackageBookingForm
from datetime import datetime, timedelta
from flask_mail import Message

public_bp = Blueprint("public", __name__)


# ----------------------------
# HOME PAGE (UPDATED WITH REVIEWS)
# ----------------------------
@public_bp.route("/", methods=["GET"])
def home():
    services = Service.query.limit(4).all()
    packages = Package.query.limit(4).all()
    gallery_items = GalleryImage.query.order_by(GalleryImage.id.desc()).limit(4).all()

    # Total gallery count
    total_gallery_count = GalleryImage.query.count()

    contact_form = ContactForm(prefix="contact")
    
    # ✅ UPDATED: Get approved reviews for homepage (limited to 4)
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).limit(3).all()
    
    # ✅ NEW: Get total approved reviews count
    total_reviews_count = Review.query.filter_by(is_approved=True).count()

    return render_template(
        "public/index.html",
        services=services,
        packages=packages,
        gallery_items=gallery_items,
        total_gallery_count=total_gallery_count,
        contact_form=contact_form,
        reviews=reviews,  # Pass reviews to template
        total_reviews_count=total_reviews_count  # ✅ NEW: Pass total count
    )


# ----------------------------
# ALL SERVICES PAGE
# ----------------------------
@public_bp.route("/services")
def services_page():
    services = Service.query.all()
    return render_template("public/services.html", services=services)


@public_bp.route("/services/<int:service_id>")
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)

    other_services = (
        Service.query
        .filter(Service.id != service_id)
        .all()
    )

    return render_template(
        "public/service_detail.html",
        service=service,
        other_services=other_services
    )


# ----------------------------
# ALL PACKAGES PAGE
# ----------------------------
@public_bp.route("/packages")
def packages_page():
    packages = (
        Package.query
        .filter_by(is_active=True)
        .order_by(Package.created_at.desc())
        .all()
    )

    return render_template(
        "public/package.html",
        packages=packages
    )


# ----------------------------
# PACKAGE DETAIL PAGE
# ----------------------------
@public_bp.route("/packages/<int:package_id>")
def package_details(package_id):
    package = (
        Package.query
        .filter_by(id=package_id, is_active=True)
        .first_or_404()
    )

    related_packages = (
        Package.query
        .filter(
            Package.id != package_id,
            Package.is_active == True
        )
        .limit(3)
        .all()
    )

    return render_template(
        "public/package_details.html",
        package=package,
        related_packages=related_packages
    )


# ----------------------------
# PACKAGE BOOKING PAGE
# ----------------------------
@public_bp.route("/packages/<int:package_id>/book", methods=["GET", "POST"])
def package_booking(package_id):
    """Handle package booking - endpoint: public.package_booking"""
    package = Package.query.get_or_404(package_id)

    form = PackageBookingForm()
    
    # Pre-populate package_id on GET request
    if request.method == 'GET':
        form.package_id.data = package.id  

    if form.validate_on_submit():
        try:
            # Calculate dates
            start_date = datetime.utcnow().date()
            expiry_date = start_date + timedelta(days=package.validity_days)

            # Create purchase record
            purchase = PackagePurchase(
                full_name=form.full_name.data.strip(),
                phone=form.phone.data.strip(),
                email=form.email.data.strip().lower(),
                package_id=form.package_id.data,
                total_uses=package.total_uses,
                remaining_uses=package.total_uses,
                start_date=start_date,
                expiry_date=expiry_date,
                status="Active"
            )

            db.session.add(purchase)
            db.session.commit()
            
            # Create notification for admin
            notification = Notification(
                type="package_booking",
                message=f"New package booking: {form.full_name.data} purchased {package.title}"
            )
            db.session.add(notification)
            db.session.commit()
            
            flash(
                f"✅ Package '{package.title}' booked successfully! "
                f"Valid until {expiry_date.strftime('%B %d, %Y')}. "
                f"You have {package.total_uses} service sessions.", 
                "success"
            )
            
            # ✅ FIXED: Use correct endpoint name
            return redirect(url_for("public.packages_page"))
        
        except Exception as e:
            db.session.rollback()
            flash("❌ An error occurred while processing your booking. Please try again.", "danger")
            print(f"Package Booking Error: {e}")  # Log the error
    
    # Display form validation errors
    if form.errors:
        for field, errors in form.errors.items():
            for error in errors:
                field_name = field.replace('_', ' ').title()
                flash(f"❌ {field_name}: {error}", "danger")

    return render_template(
        "public/package_booking.html",
        package=package,
        package_booking_form=form
    )


# ----------------------------
# CONTACT FORM SUBMIT
# ----------------------------
@public_bp.route("/contact", methods=["POST"])
def contact_submit():
    contact_form = ContactForm(prefix="contact")

    if contact_form.validate_on_submit():
        try:
            msg = ContactMessage(
                name=contact_form.name.data,
                email=contact_form.email.data,
                phone=contact_form.phone.data,
                message=contact_form.message.data,
            )
            db.session.add(msg)
            
            note = Notification(
                type="contact",
                message=f"New contact message from {contact_form.name.data}",
            )
            db.session.add(note)
            
            # Admin email
            admin_email = Message(
                subject=f"New Contact – {contact_form.name.data}",
                sender=current_app.config["MAIL_USERNAME"],
                recipients=[current_app.config["MAIL_USERNAME"]],
                reply_to=contact_form.email.data,
                body=f"""
Name: {contact_form.name.data}
Email: {contact_form.email.data}
Phone: {contact_form.phone.data}

Message:
{contact_form.message.data}
"""
            )
            mail.send(admin_email)

            # Reply email
            reply_email = Message(
                subject="Thanks for contacting us!",
                sender=current_app.config["MAIL_USERNAME"],
                recipients=[contact_form.email.data],
                body=f"""
Hi {contact_form.name.data},

Thank you for contacting us.
We have received your message and will get back to you shortly.

— SPEED 'N' SHINE
"""
            )
            mail.send(reply_email)

            db.session.commit()

            flash("Thank you! We'll contact you soon.", "success")
        
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            print(f"Contact Form Error: {e}")
    else:
        flash("Please correct contact form errors.", "danger")

    return redirect(url_for("public.home"))


# ----------------------------
# BOOKING PAGE
# ----------------------------
@public_bp.route("/booking", methods=["GET", "POST"])
def booking_page():
    services = Service.query.all()
    booking_form = BookingForm()
    booking_form.service_id.choices = [(s.id, s.name) for s in services]
    
    if booking_form.validate_on_submit():
        try:
            booking = Booking(
                full_name=booking_form.full_name.data,
                phone=booking_form.phone.data,
                email=booking_form.email.data,
                date=booking_form.date.data,
                time=booking_form.time.data,
                service_id=booking_form.service_id.data
            )

            db.session.add(booking)

            notification = Notification(
                type="booking",
                message=f"New booking from {booking.full_name} for {booking.date} at {booking.time}"
            )
            db.session.add(notification)
            db.session.commit()

            flash("🎉 Booking successful! We will contact you shortly.", "success")
            return redirect(url_for("public.booking_page"))
        
        except Exception as e:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            print(f"Booking Error: {e}")

    return render_template(
        "public/booking.html",
        booking_form=booking_form,
        services=services
    )


# ===============================
# REVIEW ROUTES
# ===============================
@public_bp.route('/add-review', methods=['GET', 'POST'])
def add_review():
    """Page where users submit reviews"""
    form = ReviewForm()
    
    if form.validate_on_submit():
        try:
            review = Review(
                name=form.name.data,
                display_name=form.display_name.data if form.display_name.data else None,
                email=form.email.data,
                phone=form.phone.data,
                review_text=form.review_text.data,
                rating=form.rating.data
            )
            
            db.session.add(review)
            
            # Create notification for admin
            notification = Notification(
                type="review",
                message=f"New review from {form.name.data} - {form.rating.data} stars"
            )
            db.session.add(notification)
            
            db.session.commit()
            
            flash('✅ Thank you for your review! It has been submitted for approval.', 'success')
            return redirect(url_for('public.home') + '#reviews')
        
        except Exception as e:
            db.session.rollback()
            flash('❌ An error occurred. Please try again.', 'danger')
            print(f"Review Submission Error: {e}")
    
    return render_template('public/add_review.html', form=form)


# ✅ ALL REVIEWS PAGE
@public_bp.route('/reviews')
def all_reviews():
    """Page displaying all approved reviews"""
    reviews = Review.query.filter_by(is_approved=True).order_by(Review.created_at.desc()).all()
    total_reviews_count = len(reviews)
    
    # Calculate average rating
    if total_reviews_count > 0:
        average_rating = sum(r.rating for r in reviews) / total_reviews_count
    else:
        average_rating = 0
    
    return render_template(
        'public/all_reviews.html',
        reviews=reviews,
        total_reviews_count=total_reviews_count,
        average_rating=average_rating
    )