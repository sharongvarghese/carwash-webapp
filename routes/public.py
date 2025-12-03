# routes/public.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from extensions import db
from models import Service, Package, Booking, Notification, ContactMessage, GalleryImage
from forms.public_forms import ContactForm, BookingForm

public_bp = Blueprint("public", __name__)


# ----------------------------
# HOME PAGE
# ----------------------------
@public_bp.route("/", methods=["GET"])
def home():
    services = Service.query.limit(4).all()
    packages = Package.query.all()
    gallery_images = GalleryImage.query.all()

    contact_form = ContactForm(prefix="contact")

    return render_template(
        "public/index.html",
        services=services,
        packages=packages,
        gallery_images=gallery_images,
        contact_form=contact_form,
    )


# ----------------------------
# ALL SERVICES PAGE
# ----------------------------
@public_bp.route("/services")
def services_page():
    services = Service.query.all()
    return render_template("public/services.html", services=services)


# ----------------------------
# SERVICE DETAIL PAGE
# ----------------------------
@public_bp.route("/service/<int:service_id>")
def service_detail(service_id):
    service = Service.query.get_or_404(service_id)
    other_services = Service.query.filter(Service.id != service_id).all()

    return render_template(
        "public/service_detail.html",
        service=service,
        other_services=other_services
    )


# ----------------------------
# CONTACT FORM SUBMIT
# ----------------------------
@public_bp.route("/contact", methods=["POST"])
def contact_submit():
    contact_form = ContactForm(prefix="contact")

    if contact_form.validate_on_submit():
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
    else:
        flash("Please correct contact form errors.", "danger")

    return redirect(url_for("public.home") + "#contact")


# ----------------------------
# BOOKING (AJAX SUPPORTED)
# ----------------------------
@public_bp.route("/booking", methods=["GET", "POST"])
def booking_page():
    services = Service.query.all()
    booking_form = BookingForm()

    booking_form.service_id.choices = [(s.id, s.name) for s in services]

    # # Debug logs
    # if request.method == "POST":
    #     print("---- NEW BOOKING SUBMISSION ----")
    #     print("Form Data:", request.form)
    #     print("Full Name:", booking_form.full_name.data)
    #     print("Phone:", booking_form.phone.data)
    #     print("Email:", booking_form.email.data)
    #     print("Date:", booking_form.date.data)
    #     print("Time:", booking_form.time.data)
    #     print("Service:", booking_form.service_id.data)
    #     print("Validate:", booking_form.validate_on_submit())
    #     print("Errors:", booking_form.errors)

    # ---------- AJAX SUBMISSION ----------
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":

        if not booking_form.validate():
            return jsonify({
                "success": False,
                "errors": booking_form.errors
            }), 400

        booking = Booking(
            full_name=booking_form.full_name.data,
            phone=booking_form.phone.data,
            email=booking_form.email.data,
            service_id=booking_form.service_id.data,
            date=booking_form.date.data,
            time=booking_form.time.data,
        )

        db.session.add(booking)

        # Notification for admin
        note = Notification(
            type="booking",
            message=f"New booking from {booking.full_name} for {booking.date} at {booking.time}",
        )
        db.session.add(note)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Slot booked successfully! We'll contact you soon."
        })

    # ---------- NORMAL PAGE LOAD ----------
    return render_template(
        "public/booking.html",
        booking_form=booking_form,
        services=services,
    )
