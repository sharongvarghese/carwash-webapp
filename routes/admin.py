# routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import AdminUser, Service, Package, Booking, Notification, GalleryImage, ContactMessage, Review, PackagePurchase, Stock, StockTransaction
from forms.admin_forms import AdminLoginForm, ServiceForm, PackageForm, GalleryUploadForm, StockForm, StockTransactionForm
from werkzeug.utils import secure_filename
from datetime import datetime, date
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
    
    # Redirect based on notification type
    if note.type == "contact":
        return redirect(url_for("admin.contact_inbox"))
    elif note.type == "booking":
        return redirect(url_for("admin.bookings"))
    elif note.type == "package_booking": 
        # If there's a reference_id (booking_id), go to detail page
        if note.reference_id:
            return redirect(url_for("admin.package_booking_detail", booking_id=note.reference_id))
        else:
            # Otherwise go to package bookings list
            return redirect(url_for("admin.package_bookings"))
    elif note.type == "review":
        return redirect(url_for("admin.reviews_panel"))
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
        image_url = None

        if image_file:
            upload_folder = os.path.join("static", "uploads", "services")
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(image_file.filename)
            image_path = os.path.join(upload_folder, filename)
            image_file.save(image_path)

            # Save relative path
            image_url = f"uploads/services/{filename}"

        # 2️⃣ SAVE TO DB (WITH DISCOUNT PRICE)
        new_service = Service(
            name=form.name.data,
            price=form.price.data,
            discount_price=form.discount_price.data,
            description=form.description.data,
            image_url=image_url
        )

        db.session.add(new_service)
        db.session.commit()

        flash("Service added successfully!", "success")
        return redirect(url_for("admin.manage_services"))

    return render_template(
        "admin/services.html",
        form=form,
        services=services
    )


@admin_bp.route("/services/delete/<int:service_id>", methods=["POST"])
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)

    # Prevent delete if bookings exist
    if service.bookings:
        flash(
            "Cannot delete service with existing bookings. Please cancel or reassign the bookings first.",
            "error"
        )
        return redirect(url_for("admin.manage_services"))

    # Delete image if exists
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
        service.discount_price = form.discount_price.data
        service.description = form.description.data

        # Handle new image upload
        if form.image.data:
            upload_folder = os.path.join("static", "uploads", "services")
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(upload_folder, filename)
            form.image.data.save(image_path)

            service.image_url = f"uploads/services/{filename}"

        db.session.commit()
        flash("Service updated successfully!", "success")
        return redirect(url_for("admin.manage_services"))

    return render_template(
        "admin/edit_service.html",
        form=form,
        service=service
    )


# =========================
# PACKAGES MANAGEMENT
# =========================
@admin_bp.route("/packages", methods=["GET", "POST"])
@login_required
def manage_packages():
    form = PackageForm()
    packages = Package.query.order_by(Package.created_at.desc()).all()

    if form.validate_on_submit():
        image_url = None

        if form.image.data:
            file = form.image.data
            filename = secure_filename(file.filename)

            upload_folder = os.path.join("static", "uploads", "packages")
            os.makedirs(upload_folder, exist_ok=True)

            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            image_url = f"uploads/packages/{filename}"

        package = Package(
            title=form.title.data,
            included_uses=form.included_uses.data,
            validity_days=form.validity_days.data,
            price=form.price.data,
            discount_price=form.discount_price.data,
            details=form.details.data,
            badge=form.badge.data,
            is_active=form.is_active.data,
            image_url=image_url
        )

        db.session.add(package)
        db.session.commit()

        flash("Package added successfully!", "success")
        return redirect(url_for("admin.manage_packages"))

    return render_template(
        "admin/packages.html",
        form=form,
        packages=packages
    )

# =========================
# EDIT PACKAGE
# =========================
@admin_bp.route("/packages/edit/<int:package_id>", methods=["GET", "POST"])
@login_required
def edit_package(package_id):
    package = Package.query.get_or_404(package_id)
    form = PackageForm(obj=package)

    if form.validate_on_submit():
        package.title = form.title.data
        package.included_uses = form.included_uses.data
        package.validity_days = form.validity_days.data
        package.price = form.price.data
        package.discount_price = form.discount_price.data
        package.details = form.details.data
        package.badge = form.badge.data
        package.is_active = form.is_active.data

        if form.image.data:
            upload_folder = os.path.join("static", "uploads", "packages")
            os.makedirs(upload_folder, exist_ok=True)

            filename = secure_filename(form.image.data.filename)
            image_path = os.path.join(upload_folder, filename)
            form.image.data.save(image_path)

            package.image_url = f"uploads/packages/{filename}"

        db.session.commit()
        flash("Package updated successfully!", "success")
        return redirect(url_for("admin.manage_packages"))

    return render_template(
        "admin/edit_package.html",
        form=form,
        package=package
    )


# =========================
# DELETE PACKAGE
# =========================

@admin_bp.route("/packages/delete/<int:package_id>", methods=["POST"])
@login_required
def delete_package(package_id):
    package = Package.query.get_or_404(package_id)

    package.is_active = False
    db.session.commit()

    flash("Package disabled successfully!", "info")
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

# ===============================
# PACKAGE BOOKINGS MANAGEMENT
# ===============================

@admin_bp.route('/package-bookings')
@login_required
def package_bookings():
    """Display all package bookings"""
    # Get filter parameter
    status_filter = request.args.get('status', 'all')
    
    # Base query
    query = PackagePurchase.query
    
    # Apply filters
    if status_filter == 'active':
        query = query.filter(
            PackagePurchase.remaining_uses > 0,
            PackagePurchase.expiry_date >= date.today()
        )
    elif status_filter == 'expired':
        query = query.filter(PackagePurchase.expiry_date < date.today())
    elif status_filter == 'completed':
        query = query.filter(PackagePurchase.remaining_uses <= 0)
    
    # Get all bookings ordered by most recent
    bookings = query.order_by(PackagePurchase.created_at.desc()).all()
    
    # Update statuses automatically
    for booking in bookings:
        old_status = booking.status
        new_status = booking.auto_status
        if old_status != new_status:
            booking.status = new_status
    
    # ✅ AUTO-MARK ALL PACKAGE BOOKING NOTIFICATIONS AS READ
    unread_package_notifications = Notification.query.filter_by(
        type="package_booking",
        is_read=False
    ).all()
    
    for notification in unread_package_notifications:
        notification.is_read = True
    
    if unread_package_notifications:
        db.session.commit()
    else:
        db.session.commit()
    
    # Count statistics
    total_bookings = PackagePurchase.query.count()
    active_bookings = PackagePurchase.query.filter(
        PackagePurchase.remaining_uses > 0,
        PackagePurchase.expiry_date >= date.today()
    ).count()
    expired_bookings = PackagePurchase.query.filter(
        PackagePurchase.expiry_date < date.today()
    ).count()
    completed_bookings = PackagePurchase.query.filter(
        PackagePurchase.remaining_uses <= 0
    ).count()
    
    return render_template(
        'admin/package_bookings.html',
        bookings=bookings,
        status_filter=status_filter,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        expired_bookings=expired_bookings,
        completed_bookings=completed_bookings
    )


@admin_bp.route('/package-bookings/<int:booking_id>')
@login_required
def package_booking_detail(booking_id):
    """View detailed information about a package booking"""
    booking = PackagePurchase.query.get_or_404(booking_id)
    
    # Update status
    booking.status = booking.auto_status
    db.session.commit()
    
    return render_template(
        'admin/package_booking_detail.html',
        booking=booking
    )


@admin_bp.route('/package-bookings/<int:booking_id>/update-remaining', methods=['POST'])
@login_required
def update_remaining_uses(booking_id):
    """Update remaining uses for a package booking"""
    booking = PackagePurchase.query.get_or_404(booking_id)
    
    # Get the action from form
    action = request.form.get('action')
    
    if action == 'decrement':
        if booking.remaining_uses > 0:
            booking.remaining_uses -= 1
            flash(f'✅ Service session recorded. {booking.remaining_uses} sessions remaining.', 'success')
        else:
            flash('⚠️ No remaining sessions to deduct.', 'warning')
    
    elif action == 'increment':
        if booking.remaining_uses < booking.total_uses:
            booking.remaining_uses += 1
            flash(f'✅ Session restored. {booking.remaining_uses} sessions remaining.', 'success')
        else:
            flash('⚠️ Cannot exceed total sessions.', 'warning')
    
    elif action == 'manual':
        try:
            new_value = int(request.form.get('remaining_uses', 0))
            if 0 <= new_value <= booking.total_uses:
                old_value = booking.remaining_uses
                booking.remaining_uses = new_value
                flash(f'✅ Remaining sessions updated from {old_value} to {new_value}.', 'success')
            else:
                flash(f'⚠️ Value must be between 0 and {booking.total_uses}.', 'warning')
        except ValueError:
            flash('❌ Invalid value provided.', 'danger')
    
    # Update status
    booking.status = booking.auto_status
    booking.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    # Check if referrer is detail page
    if 'package_booking_detail' in request.referrer:
        return redirect(url_for('admin.package_booking_detail', booking_id=booking_id))
    
    return redirect(url_for('admin.package_bookings'))


@admin_bp.route('/package-bookings/<int:booking_id>/delete', methods=['POST'])
@login_required
def delete_package_booking(booking_id):
    """Delete a package booking"""
    booking = PackagePurchase.query.get_or_404(booking_id)
    
    customer_name = booking.full_name
    
    db.session.delete(booking)
    db.session.commit()
    
    flash(f'✅ Package booking for {customer_name} has been deleted.', 'success')
    return redirect(url_for('admin.package_bookings'))


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


# ===============================
# NEW: REVIEWS MANAGEMENT
# ===============================

@admin_bp.route("/reviews")
@login_required
def reviews_panel():
    """Admin panel to view all reviews"""
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    
    # ✅ AUTO-MARK ALL REVIEW NOTIFICATIONS AS READ
    unread_review_notifications = Notification.query.filter_by(
        type="review",
        is_read=False
    ).all()
    
    for notification in unread_review_notifications:
        notification.is_read = True
    
    if unread_review_notifications:
        db.session.commit()
    
    return render_template("admin/reviews_panel.html", reviews=reviews)


@admin_bp.route("/reviews/delete/<int:review_id>", methods=["POST"])
@login_required
def delete_review(review_id):
    """Delete a review"""
    review = Review.query.get_or_404(review_id)
    
    db.session.delete(review)
    db.session.commit()
    
    flash('Review deleted successfully.', 'success')
    return redirect(url_for('admin.reviews_panel'))


@admin_bp.route('/stock', methods=['GET', 'POST'])
@login_required
def stock_management():
    """Stock management page"""
    form = StockForm()
    
    if form.validate_on_submit():
        # Create new stock item
        stock = Stock(
            item_name=form.item_name.data,
            category=form.category.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            notes=form.notes.data
        )
        db.session.add(stock)
        
        # Create initial transaction
        transaction = StockTransaction(
            stock=stock,
            transaction_type='add',
            quantity=form.quantity.data,
            previous_quantity=0,
            new_quantity=form.quantity.data,
            reason='Initial stock entry'
        )
        db.session.add(transaction)
        
        db.session.commit()
        flash(f'Stock item "{stock.item_name}" added successfully!', 'success')
        return redirect(url_for('admin.stock_management'))
    
    # Get filter parameters
    category_filter = request.args.get('category', 'all')
    status_filter = request.args.get('status', 'all')
    
    # Base query
    query = Stock.query
    
    # Apply category filter
    if category_filter != 'all':
        query = query.filter_by(category=category_filter)
    
    # Apply status filter
    if status_filter == 'low':
        query = query.filter(Stock.quantity > 0, Stock.quantity <= 5)
    elif status_filter == 'out':
        query = query.filter_by(quantity=0)
    
    stocks = query.order_by(Stock.item_name).all()
    
    # Calculate statistics
    all_stocks = Stock.query.all()
    total_items = len(all_stocks)
    low_stock_items = sum(1 for s in all_stocks if s.is_low_stock)
    out_of_stock_items = sum(1 for s in all_stocks if s.quantity == 0)
    
    return render_template('admin/stock_management.html',
                         form=form,
                         stocks=stocks,
                         total_items=total_items,
                         low_stock_items=low_stock_items,
                         out_of_stock_items=out_of_stock_items,
                         category_filter=category_filter,
                         status_filter=status_filter)


@admin_bp.route('/stock/<int:stock_id>', methods=['GET', 'POST'])
@login_required
def stock_detail(stock_id):
    """Stock detail and transaction page"""
    stock = Stock.query.get_or_404(stock_id)
    form = StockTransactionForm()
    
    if form.validate_on_submit():
        transaction_type = form.transaction_type.data
        quantity = form.quantity.data
        previous_quantity = stock.quantity
        
        # Calculate new quantity based on transaction type
        if transaction_type == 'add':
            new_quantity = previous_quantity + quantity
        elif transaction_type == 'reduce':
            if quantity > previous_quantity:
                flash('Cannot reduce more than available stock!', 'error')
                return redirect(url_for('admin.stock_detail', stock_id=stock_id))
            new_quantity = previous_quantity - quantity
        else:  # adjust
            new_quantity = quantity
        
        # Update stock
        stock.quantity = new_quantity
        
        # Create transaction record
        transaction = StockTransaction(
            stock_id=stock.id,
            transaction_type=transaction_type,
            quantity=quantity,
            previous_quantity=previous_quantity,
            new_quantity=new_quantity,
            reason=form.reason.data
        )
        db.session.add(transaction)
        db.session.commit()
        
        flash(f'Stock updated successfully! New quantity: {new_quantity} {stock.unit}', 'success')
        return redirect(url_for('admin.stock_detail', stock_id=stock_id))
    
    # Get transaction history
    transactions = stock.transactions.limit(20).all()
    
    return render_template('admin/stock_details.html',
                         stock=stock,
                         form=form,
                         transactions=transactions)


@admin_bp.route('/stock/<int:stock_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_stock(stock_id):
    """Edit stock item details"""
    stock = Stock.query.get_or_404(stock_id)
    form = StockForm(obj=stock)
    
    if form.validate_on_submit():
        old_quantity = stock.quantity
        
        stock.item_name = form.item_name.data
        stock.category = form.category.data
        stock.quantity = form.quantity.data
        stock.unit = form.unit.data
        stock.notes = form.notes.data
        
        # If quantity changed, create a transaction
        if old_quantity != form.quantity.data:
            transaction = StockTransaction(
                stock_id=stock.id,
                transaction_type='adjust',
                quantity=abs(form.quantity.data - old_quantity),
                previous_quantity=old_quantity,
                new_quantity=form.quantity.data,
                reason='Manual adjustment via edit'
            )
            db.session.add(transaction)
        
        db.session.commit()
        flash(f'Stock item "{stock.item_name}" updated successfully!', 'success')
        return redirect(url_for('admin.stock_detail', stock_id=stock_id))
    
    return render_template('admin/edit_stock_form.html', form=form, stock=stock)


@admin_bp.route('/stock/<int:stock_id>/delete', methods=['POST'])
@login_required
def delete_stock(stock_id):
    """Delete stock item"""
    stock = Stock.query.get_or_404(stock_id)
    item_name = stock.item_name
    
    # Delete all transactions first
    StockTransaction.query.filter_by(stock_id=stock_id).delete()
    
    # Delete stock item
    db.session.delete(stock)
    db.session.commit()
    
    flash(f'Stock item "{item_name}" deleted successfully!', 'success')
    return redirect(url_for('admin.stock_management'))


@admin_bp.route('/stock/<int:stock_id>/quick-reduce', methods=['POST'])
@login_required
def quick_reduce_stock(stock_id):
    """Quick reduce stock quantity"""
    stock = Stock.query.get_or_404(stock_id)
    quantity = float(request.form.get('quantity', 0))
    
    if quantity <= 0:
        flash('Invalid quantity!', 'error')
        return redirect(url_for('admin.stock_management'))
    
    if quantity > stock.quantity:
        flash('Cannot reduce more than available stock!', 'error')
        return redirect(url_for('admin.stock_management'))
    
    previous_quantity = stock.quantity
    new_quantity = previous_quantity - quantity
    
    # Update stock
    stock.quantity = new_quantity
    
    # Create transaction
    transaction = StockTransaction(
        stock_id=stock.id,
        transaction_type='reduce',
        quantity=quantity,
        previous_quantity=previous_quantity,
        new_quantity=new_quantity,
        reason='Quick reduce from stock list'
    )
    db.session.add(transaction)
    db.session.commit()
    
    flash(f'Reduced {quantity} {stock.unit} from {stock.item_name}', 'success')
    return redirect(url_for('admin.stock_management'))