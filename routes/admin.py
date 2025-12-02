# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import AdminUser, Service, Package, Booking, Notification, GalleryImage
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
# MARK NOTIFICATION AS READ
# =========================
@admin_bp.route("/notifications/read/<int:note_id>")
@login_required
def mark_notification_read(note_id):
    note = Notification.query.get_or_404(note_id)
    note.is_read = True
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


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



@admin_bp.route("/services/delete/<int:service_id>")
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    db.session.delete(service)
    db.session.commit()
    flash("Service deleted.", "info")
    return redirect(url_for("admin.manage_services"))


# =========================
# PACKAGES MANAGEMENT
# =========================
@admin_bp.route("/packages", methods=["GET", "POST"])
@login_required
def manage_packages():
    form = PackageForm()
    packages = Package.query.all()

    if form.validate_on_submit():
        package = Package(
            title=form.title.data,
            details=form.details.data,
            price=form.price.data,
            discount_price=form.discount_price.data,
            image_url=form.image_url.data,
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
    db.session.delete(package)
    db.session.commit()
    flash("Package deleted.", "info")
    return redirect(url_for("admin.manage_packages"))


# =========================
# BOOKINGS
# =========================
@admin_bp.route("/bookings")
@login_required
def bookings():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template("admin/bookings.html", bookings=bookings)


@admin_bp.route("/bookings/status/<int:booking_id>/<status>")
@login_required
def update_booking_status(booking_id, status):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = status
    db.session.commit()
    flash("Booking status updated.", "success")
    return redirect(url_for("admin.bookings"))


# =========================
# GALLERY ADMIN
# =========================
@admin_bp.route("/gallery", methods=["GET", "POST"])
@login_required
def admin_gallery():
    form = GalleryUploadForm()

    if form.validate_on_submit():
        file = form.image.data
        filename = secure_filename(file.filename)

        # save image to static/uploads
        upload_folder = os.path.join("static", "uploads")
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)

        new_image = GalleryImage(
            image_url=f"uploads/{filename}",
            caption=form.caption.data,
        )
        db.session.add(new_image)
        db.session.commit()

        flash("Image uploaded successfully!", "success")
        return redirect(url_for("admin.admin_gallery"))

    images = GalleryImage.query.order_by(GalleryImage.created_at.desc()).all()

    return render_template("admin/gallery.html", form=form, images=images)


@admin_bp.route("/gallery/delete/<int:image_id>", methods=["POST"])
@login_required
def delete_gallery_image(image_id):
    image = GalleryImage.query.get_or_404(image_id)

    # delete physical file
    try:
        os.remove(os.path.join("static", image.image_url))
    except:
        pass

    db.session.delete(image)
    db.session.commit()

    flash("Image deleted.", "success")
    return redirect(url_for("admin.admin_gallery"))
