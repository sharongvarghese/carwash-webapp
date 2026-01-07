# routes/public.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from extensions import db, mail
from models import Service, Package, Booking, Notification, ContactMessage, GalleryImage
from forms.public_forms import ContactForm, BookingForm
from flask_mail import Message

public_bp = Blueprint("public", __name__)


# ----------------------------
# HOME PAGE
# ----------------------------
@public_bp.route("/", methods=["GET"])
def home():
    services = Service.query.limit(4).all()
    packages = Package.query.limit(4).all()
    gallery_items = GalleryImage.query.order_by(GalleryImage.id.desc()).limit(4).all()

    # Total gallery count
    total_gallery_count = GalleryImage.query.count()

    contact_form = ContactForm(prefix="contact")

    return render_template(
        "public/index.html",
        services=services,
        packages=packages,
        gallery_items=gallery_items,
        total_gallery_count=total_gallery_count,
        contact_form=contact_form,
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
        other_services = other_services
    )


    


# ----------------------------
# ALL PACKAGES PAGE
# ----------------------------
@public_bp.route('/packages')
def packages_page():
    packages = Package.query.all()  
    return render_template('public/package.html', packages=packages)   

# ----------------------------
# PACKAGE DETAIL PAGE
# ----------------------------
@public_bp.route("/packages/<int:package_id>")
def package_details(package_id):
    package = Package.query.get_or_404(package_id)

    related_packages = (
        Package.query
        .filter(Package.id != package_id)
        .limit(3)
        .all()
    )

    return render_template(
        "public/package_details.html",
        package=package,
        related_packages=related_packages
    )




# ----------------------------
# CONTACT FORM SUBMIT
# ----------------------------
@public_bp.route("/contact", methods=["POST"])
def contact_submit():
    contact_form = ContactForm(prefix="contact")

    if contact_form.validate_on_submit():
        # 1️⃣ SAVE MESSAGE TO DB
        msg = ContactMessage(
            name=contact_form.name.data,
            email=contact_form.email.data,
            phone=contact_form.phone.data,
            message=contact_form.message.data,
        )
        db.session.add(msg)

        # 2️⃣ CREATE ADMIN NOTIFICATION
        note = Notification(
            type="contact",
            message=f"New contact message from {contact_form.name.data}",
        )
        db.session.add(note)

        # 3️⃣ SEND EMAIL TO ADMIN 🔥
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

        # 4️⃣ AUTO-REPLY TO USER (OPTIONAL BUT PROFESSIONAL)
        reply_email = Message(
            subject="Thanks for contacting us!",
            sender=current_app.config["MAIL_USERNAME"],
            recipients=[contact_form.email.data],
            body=f"""
Hi {contact_form.name.data},

Thank you for contacting us.
We have received your message and will get back to you shortly.

— Golden Touch Car Wash
"""
        )
        mail.send(reply_email)

        # 5️⃣ COMMIT EVERYTHING
        db.session.commit()

        flash("Thank you! We’ll contact you soon.", "success")
    else:
        flash("Please correct contact form errors.", "danger")

    return redirect(url_for("public.home") + "#contact")



@public_bp.route("/booking", methods=["GET", "POST"])
def booking_page():

    services = Service.query.all()
    booking_form = BookingForm()
    booking_form.service_id.choices = [(s.id, s.name) for s in services]
    if booking_form.validate_on_submit():
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

    return render_template(
        "public/booking.html",
        booking_form=booking_form,
        services=services
    )

