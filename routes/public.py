# routes/public.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from extensions import db
from models import Service, Package, Booking, Notification, ContactMessage
from forms.public_forms import ContactForm, BookingForm

public_bp = Blueprint("public", __name__)


@public_bp.route("/", methods=["GET", "POST"])
def home():
    services = Service.query.all()
    packages = Package.query.all()

    contact_form = ContactForm(prefix="contact")
    booking_form = BookingForm(prefix="booking")

    # populate service choices for booking
    booking_form.service_id.choices = [(s.id, s.name) for s in services]

    # CONTACT FORM
    if contact_form.submit.data and contact_form.validate_on_submit():
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
        db.session.commit()

        flash("Thank you! We’ll contact you soon.", "success")
        return redirect(url_for("public.home") + "#contact")

    # BOOKING FORM
    if booking_form.submit.data and booking_form.validate_on_submit():
        booking = Booking(
            full_name=booking_form.full_name.data,
            phone=booking_form.phone.data,
            email=booking_form.email.data,
            service_id=booking_form.service_id.data or None,
            date=booking_form.date.data,
            time=booking_form.time.data,
        )
        db.session.add(booking)

        note = Notification(
            type="booking",
            message=f"New booking from {booking_form.full_name.data} for {booking_form.date.data} at {booking_form.time.data}",
        )
        db.session.add(note)
        db.session.commit()

        flash("Slot booked successfully! We’ll contact you soon.", "success")
        return redirect(url_for("public.home") + "#booking")

    # If POST and invalid
    if request.method == "POST":
        if contact_form.submit.data and not contact_form.validate():
            flash("Please correct contact form errors.", "danger")
        elif booking_form.submit.data and not booking_form.validate():
            flash("Please correct booking form errors.", "danger")

    return render_template(
        "public/index.html",
        services=services,
        packages=packages,
        contact_form=contact_form,
        booking_form=booking_form,
    )
