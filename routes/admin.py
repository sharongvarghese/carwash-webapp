# routes/admin.py
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
)
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import AdminUser, Service, Package, Booking, Notification
from forms.admin_forms import AdminLoginForm, ServiceForm, PackageForm

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


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
        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html", form=form)


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("admin.login"))


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


@admin_bp.route("/notifications/read/<int:note_id>")
@login_required
def mark_notification_read(note_id):
    note = Notification.query.get_or_404(note_id)
    note.is_read = True
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/services", methods=["GET", "POST"])
@login_required
def manage_services():
    form = ServiceForm()
    services = Service.query.all()

    if form.validate_on_submit():
        service = Service(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            image_url=form.image_url.data,
        )
        db.session.add(service)
        db.session.commit()
        flash("Service added.", "success")
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
        flash("Package added.", "success")
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
