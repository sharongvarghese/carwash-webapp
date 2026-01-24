# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import AdminUser, Service, Package, Booking, Notification, GalleryImage, ContactMessage
from forms.admin_forms import AdminLoginForm, ServiceForm, PackageForm, GalleryUploadForm
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# =========================
# LOGIN
# =========================
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = AdminLoginForm()
    if form.validate_on_submit():
        user = AdminUser.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("admin/login.html", form=form)


# =========================
# LOGOUT
# =========================
@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))


# =========================
# DASHBOARD
# =========================
@admin_bp.route("/")
@login_required
def dashboard():
    booking_count = Booking.query.count()
    unread_notifications = Notification.query.filter_by(is_read=False).all()

    return render_template(
        "admin/dashboard.html",
        booking_count=booking_count,
        unread_notifications=unread_notifications,
    )


# =========================
# MARK NOTIFICATION AS READ (UPDATED)
# =========================
@admin_bp.route("/notifications/read/<int:note_id>")
@login_required
def mark_notification_read(note_id):
    note = Notification.query.get_or_404(note_id)
    note.is_read = True
    db.session.commit()
    
    # Redirect based on notification type
    if note.type == "contact":
        return redirect(url_for("admin.contact_inbox"))
    elif note.type == "booking":
        return redirect(url_for("admin.bookings"))
    else:
        return redirect(url_for("admin.dashboard"))


# =========================
# CONTACT INBOX (UPDATED - Auto-mark contact notifications as read)
# =========================
@admin_bp.route("/contacts")
@login_required
def contact_inbox():
    messages = ContactMessage.query.order_by(
        ContactMessage.created_at.desc()
    ).all()

    # ✅ AUTO-MARK ALL CONTACT NOTIFICATIONS AS READ
    unread_contact_notifications = Notification.query.filter_by(
        type="contact", 
        is_read=False
    ).all()
    
    for notification in unread_contact_notifications:
        notification.is_read = True
    
    if unread_contact_notifications:
        db.session.commit()

    return render_template(
        "admin/contact_inbox.html",
        messages=messages
    )


# =========================
# VIEW CONTACT MESSAGE
# =========================
@admin_bp.route("/contacts/<int:message_id>")
@login_required
def view_contact_message(message_id):
    message = ContactMessage.query.get_or_404(message_id)

    # Mark as read
    if not message.is_read:
        message.is_read = True
        db.session.commit()

    return render_template(
        "admin/contact_view.html",
        message=message
    )


@admin_bp.route("/contact/delete-selected", methods=["POST"])
@login_required
def delete_selected_contacts():
    ids = request.form.getlist("selected_ids")

    if not ids:
        flash("No messages selected.", "warning")
        return redirect(url_for("admin.contact_inbox"))

    ContactMessage.query.filter(
        ContactMessage.id.in_(ids)
    ).delete(synchronize_session=False)

    db.session.commit()
    flash(f"{len(ids)} message(s) deleted.", "success")

    return redirect(url_for("admin.contact_inbox"))


# =========================
# SERVICES MANAGEMENT
# =========================
@admin_bp.route("/services", methods=["GET", "POST"])
@login_required
def manage_services():
    form = ServiceForm()
    services = Service.query.all()

    if form.validate_on_submit():

        # 1️⃣ HANDLE IMAGE UPLOAD
        image_file = form.image.data
        filename = None
        
        if image_file:
            upload_folder = os.path.join("static", "uploads", "services")
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(image_file.filename)
            image_path = os.path.join(upload_folder, filename)

            image_file.save(image_path)

            # Save path relative to /static
            image_url = f"uploads/services/{filename}"
        else:
            image_url = None

        # 2️⃣ SAVE TO DB
        new_service = Service(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            image_url=image_url
        )

        db.session.add(new_service)
        db.session.commit()

        flash("Service added successfully!", "success")
        return redirect(url_for("admin.manage_services"))

    return render_template("admin/services.html", form=form, services=services)


@admin_bp.route("/services/delete/<int:service_id>", methods=["POST"])
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service.bookings:
        flash("Cannot delete service with existing bookings. Please cancel or reassign the bookings first.", "error")
        return redirect(url_for("admin.manage_services"))
    if service.image_url:
        image_path = os.path.join("static", service.image_url)  
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print("Error deleting service image:", e)
    try:
        db.session.delete(service)
        db.session.commit()
        flash("Service deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting service. Please try again.", "error")
        print("Database error:", e)
    return redirect(url_for("admin.manage_services"))


@admin_bp.route("/services/edit/<int:service_id>", methods=["GET", "POST"])
@login_required
def edit_service(service_id):
    service = Service.query.get_or_404(service_id)
    form = ServiceForm(obj=service)  
    if form.validate_on_submit():
        service.name = form.name.data
        service.price = form.price.data
        service.description = form.description.data
        if form.image.data:
            upload_folder = os.path.join("static", "uploads", "services")
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(upload_folder, filename)
            form.image.data.save(image_path)

            # save relative path
            service.image_url = f"uploads/services/{filename}"

        db.session.commit()
        flash("Service updated successfully!", "success")
        return redirect(url_for("admin.manage_services"))

    return render_template("admin/edit_service.html", form=form, service=service)


# =========================
# PACKAGES MANAGEMENT
# =========================
@admin_bp.route("/packages", methods=["GET", "POST"])
@login_required
def manage_packages():
    form = PackageForm()
    packages = Package.query.all()

    if form.validate_on_submit():
        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)

            upload_folder = os.path.join("static", "uploads", "packages")
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            image_url = f"uploads/packages/{filename}"
        else:
            image_url = None

        package = Package(
            title=form.title.data,
            details=form.details.data,
            price=form.price.data,
            discount_price=form.discount_price.data,
            image_url=image_url
        )

        db.session.add(package)
        db.session.commit()
        flash("Package added successfully!", "success")
        return redirect(url_for("admin.manage_packages"))

    return render_template("admin/packages.html", form=form, packages=packages)


@admin_bp.route("/packages/delete/<int:package_id>")
@login_required
def delete_package(package_id):
    package = Package.query.get_or_404(package_id)
    if package.image_url:
        image_path = os.path.join("static", package.image_url)  
        if os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception as e:
                print("Error deleting image:", e)
    db.session.delete(package)
    db.session.commit()
    flash("Package deleted successfully!", "info")
    return redirect(url_for("admin.manage_packages"))


# =========================
# BOOKINGS MANAGEMENT
# =========================
@admin_bp.route("/bookings")
@login_required
def bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()

    unread_booking_notifications = Notification.query.filter_by(
        type="booking",
        is_read=False
    ).all()

    for notification in unread_booking_notifications:
        notification.is_read = True

    if unread_booking_notifications:
        db.session.commit()

    return render_template("admin/bookings.html", bookings=bookings)


@admin_bp.route("/bookings/status/<int:booking_id>", methods=["POST"])
@login_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    status = request.form.get("status")

    valid_statuses = ['Pending', 'Contacted', 'Confirmed', 'Completed', 'Cancelled']
    if status not in valid_statuses:
        flash("Invalid status selected.", "error")
        return redirect(url_for("admin.bookings"))

    booking.status = status
    db.session.commit()

    flash("Booking status updated successfully!", "success")
    return redirect(url_for("admin.bookings"))


@admin_bp.route("/bookings/delete/<int:booking_id>", methods=["POST"])
@login_required
def delete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    db.session.delete(booking)
    db.session.commit()
    flash("Booking deleted successfully!", "success")
    return redirect(url_for("admin.bookings"))



# =========================
# GALLERY ADMIN
# =========================
import os
from werkzeug.utils import secure_filename
from datetime import datetime

@admin_bp.route("/gallery", methods=["GET", "POST"])
@login_required
def admin_gallery():
    form = GalleryUploadForm()

    if form.validate_on_submit():
        before = form.before_image.data
        after = form.after_image.data

        # Timestamp to avoid filename conflicts
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        before_name = f"{timestamp}_before_{secure_filename(before.filename)}"
        after_name  = f"{timestamp}_after_{secure_filename(after.filename)}"

        # Base upload directory
        base_upload = os.path.join("static", "uploads", "gallery")

        before_dir = os.path.join(base_upload, "before")
        after_dir  = os.path.join(base_upload, "after")

        # Create folders if not exist
        os.makedirs(before_dir, exist_ok=True)
        os.makedirs(after_dir, exist_ok=True)

        # Save files
        before_path = os.path.join(before_dir, before_name)
        after_path  = os.path.join(after_dir, after_name)

        before.save(before_path)
        after.save(after_path)

        # Save relative paths in DB
        gallery = GalleryImage(
            before_image=f"uploads/gallery/before/{before_name}",
            after_image=f"uploads/gallery/after/{after_name}",
            caption=form.caption.data
        )

        db.session.add(gallery)
        db.session.commit()

        flash("Gallery item added successfully!", "success")
        return redirect(url_for("admin.admin_gallery"))

    gallery_items = GalleryImage.query.order_by(
        GalleryImage.created_at.desc()
    ).all()

    return render_template(
        "admin/gallery.html",
        form=form,
        gallery_items=gallery_items
    )


@admin_bp.route("/gallery/delete/<int:image_id>", methods=["POST"])
@login_required
def delete_gallery_image(image_id):
    item = GalleryImage.query.get_or_404(image_id)

    for img in [item.before_image, item.after_image]:
        try:
            os.remove(os.path.join("static", img))
        except:
            pass

    db.session.delete(item)
    db.session.commit()

    flash("Gallery item deleted.", "success")
    return redirect(url_for("admin.admin_gallery"))