from datetime import datetime, date, timedelta
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.admin import admin_bp
from app.admin.forms import BusForm, RouteForm, ScheduleForm, UserForm
from app.auth.decorators import role_required
from app.extensions import db
from app.models.user import User
from app.models.bus import Bus
from app.models.route import Route
from app.models.schedule import Schedule
from app.models.booking import Booking
from app.models.ticket import Ticket
from app.models.payment import Payment
from sqlalchemy import func


@admin_bp.before_request
@login_required
@role_required('Administrator')
def before_request():
    pass


# ── Dashboard ──────────────────────────────────────────────
@admin_bp.route('/dashboard')
def dashboard():
    today = date.today()
    total_buses = Bus.query.count()
    total_routes = Route.query.filter_by(status='Active').count()
    today_bookings = Booking.query.filter(func.date(Booking.booking_date) == today).count()
    today_revenue = db.session.query(
        func.coalesce(func.sum(Payment.payment_amount), 0)
    ).filter(
        Payment.payment_status == 'Paid',
        func.date(Payment.payment_date) == today
    ).scalar()
    available_seats = db.session.query(
        func.coalesce(func.sum(Schedule.available_seats), 0)
    ).filter(
        Schedule.departure_date >= today,
        Schedule.status == 'Scheduled'
    ).scalar()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()

    return render_template('admin/dashboard.html',
                           total_buses=total_buses,
                           total_routes=total_routes,
                           today_bookings=today_bookings,
                           today_revenue=today_revenue,
                           available_seats=available_seats,
                           recent_bookings=recent_bookings)


# ── Bus Management ─────────────────────────────────────────
@admin_bp.route('/buses')
def buses():
    all_buses = Bus.query.order_by(Bus.bus_id.desc()).all()
    return render_template('admin/buses.html', buses=all_buses)


@admin_bp.route('/bus/add', methods=['GET', 'POST'])
def add_bus():
    form = BusForm()
    if form.validate_on_submit():
        bus = Bus(
            bus_number=form.bus_number.data,
            bus_name=form.bus_name.data,
            bus_type=form.bus_type.data,
            total_seats=form.total_seats.data,
            registration_number=form.registration_number.data,
            status=form.status.data,
        )
        db.session.add(bus)
        db.session.commit()
        flash('Bus added successfully!', 'success')
        return redirect(url_for('admin.buses'))
    return render_template('admin/bus_form.html', form=form, title='Add Bus')


@admin_bp.route('/bus/edit/<int:bus_id>', methods=['GET', 'POST'])
def edit_bus(bus_id):
    bus = db.session.get(Bus, bus_id)
    if not bus:
        flash('Bus not found.', 'danger')
        return redirect(url_for('admin.buses'))
    form = BusForm(obj=bus)
    if form.validate_on_submit():
        form.populate_obj(bus)
        db.session.commit()
        flash('Bus updated successfully!', 'success')
        return redirect(url_for('admin.buses'))
    return render_template('admin/bus_form.html', form=form, title='Edit Bus', bus=bus)


@admin_bp.route('/bus/delete/<int:bus_id>', methods=['POST'])
def delete_bus(bus_id):
    bus = db.session.get(Bus, bus_id)
    if bus:
        db.session.delete(bus)
        db.session.commit()
        flash('Bus deleted.', 'success')
    return redirect(url_for('admin.buses'))


# ── Route Management ───────────────────────────────────────
@admin_bp.route('/routes')
def routes():
    all_routes = Route.query.order_by(Route.route_id.desc()).all()
    return render_template('admin/routes.html', routes=all_routes)


@admin_bp.route('/route/add', methods=['GET', 'POST'])
def add_route():
    form = RouteForm()
    if form.validate_on_submit():
        if form.origin.data == form.destination.data:
            flash('Origin and destination cannot be the same.', 'danger')
            return render_template('admin/route_form.html', form=form, title='Add Route')
        route = Route(
            origin=form.origin.data,
            destination=form.destination.data,
            distance_km=form.distance_km.data,
            estimated_duration=form.estimated_duration.data,
            fare=form.fare.data,
            status=form.status.data,
        )
        db.session.add(route)
        db.session.commit()
        flash('Route added successfully!', 'success')
        return redirect(url_for('admin.routes'))
    return render_template('admin/route_form.html', form=form, title='Add Route')


@admin_bp.route('/route/edit/<int:route_id>', methods=['GET', 'POST'])
def edit_route(route_id):
    route = db.session.get(Route, route_id)
    if not route:
        flash('Route not found.', 'danger')
        return redirect(url_for('admin.routes'))
    form = RouteForm(obj=route)
    if form.validate_on_submit():
        form.populate_obj(route)
        db.session.commit()
        flash('Route updated!', 'success')
        return redirect(url_for('admin.routes'))
    return render_template('admin/route_form.html', form=form, title='Edit Route', route=route)


@admin_bp.route('/route/delete/<int:route_id>', methods=['POST'])
def delete_route(route_id):
    route = db.session.get(Route, route_id)
    if route:
        db.session.delete(route)
        db.session.commit()
        flash('Route deleted.', 'success')
    return redirect(url_for('admin.routes'))


# ── Schedule Management ────────────────────────────────────
@admin_bp.route('/schedules')
def schedules():
    all_schedules = Schedule.query.order_by(Schedule.departure_date.desc(), Schedule.departure_time).all()
    return render_template('admin/schedules.html', schedules=all_schedules)


@admin_bp.route('/schedule/add', methods=['GET', 'POST'])
def add_schedule():
    form = ScheduleForm()
    form.bus_id.choices = [(b.bus_id, f'{b.bus_number} - {b.bus_name} ({b.bus_type})') for b in Bus.query.filter_by(status='Available').all()]
    form.route_id.choices = [(r.route_id, f'{r.origin} → {r.destination}') for r in Route.query.filter_by(status='Active').all()]

    if form.validate_on_submit():
        bus = db.session.get(Bus, form.bus_id.data)
        schedule = Schedule(
            bus_id=form.bus_id.data,
            route_id=form.route_id.data,
            departure_date=form.departure_date.data,
            departure_time=form.departure_time.data,
            arrival_time=form.arrival_time.data,
            available_seats=bus.total_seats,
            status=form.status.data,
        )
        db.session.add(schedule)
        db.session.commit()
        flash('Schedule created!', 'success')
        return redirect(url_for('admin.schedules'))
    return render_template('admin/schedule_form.html', form=form, title='Add Schedule')


@admin_bp.route('/schedule/edit/<int:schedule_id>', methods=['GET', 'POST'])
def edit_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        flash('Schedule not found.', 'danger')
        return redirect(url_for('admin.schedules'))
    form = ScheduleForm(obj=schedule)
    form.bus_id.choices = [(b.bus_id, f'{b.bus_number} - {b.bus_name} ({b.bus_type})') for b in Bus.query.filter_by(status='Available').all()]
    form.route_id.choices = [(r.route_id, f'{r.origin} → {r.destination}') for r in Route.query.filter_by(status='Active').all()]
    if form.validate_on_submit():
        schedule.bus_id = form.bus_id.data
        schedule.route_id = form.route_id.data
        schedule.departure_date = form.departure_date.data
        schedule.departure_time = form.departure_time.data
        schedule.arrival_time = form.arrival_time.data
        schedule.status = form.status.data
        db.session.commit()
        flash('Schedule updated!', 'success')
        return redirect(url_for('admin.schedules'))
    return render_template('admin/schedule_form.html', form=form, title='Edit Schedule', schedule=schedule)


@admin_bp.route('/schedule/delete/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted.', 'success')
    return redirect(url_for('admin.schedules'))


# ── Bookings ───────────────────────────────────────────────
@admin_bp.route('/bookings')
def bookings():
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings)


# ── Payments ───────────────────────────────────────────────
@admin_bp.route('/payments')
def payments():
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('admin/payments.html', payments=all_payments)


# ── Users ──────────────────────────────────────────────────
@admin_bp.route('/users')
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)


@admin_bp.route('/user/add', methods=['GET', 'POST'])
def add_user():
    from app.auth.forms import RegisterForm
    from werkzeug.security import generate_password_hash
    form = UserForm()
    if form.validate_on_submit():
        password = request.form.get('password', 'default123')
        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            phone=form.phone.data,
            role=form.role.data,
            status=form.status.data,
            password=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()
        flash(f'User created! Default password: {password}', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, title='Add User')


@admin_bp.route('/user/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.users'))
    form = UserForm(obj=user)
    if form.validate_on_submit():
        user.full_name = form.full_name.data
        user.email = form.email.data
        user.phone = form.phone.data
        user.role = form.role.data
        user.status = form.status.data
        db.session.commit()
        flash('User updated!', 'success')
        return redirect(url_for('admin.users'))
    return render_template('admin/user_form.html', form=form, title='Edit User', user=user)


# ── Reports ────────────────────────────────────────────────
@admin_bp.route('/reports')
def reports():
    report_type = request.args.get('type', 'daily')
    today = date.today()

    if report_type == 'daily':
        start_date = today
        end_date = today
    elif report_type == 'weekly':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    else:  # monthly
        start_date = today.replace(day=1)
        end_date = today

    # Filter bookings in range
    period_bookings = Booking.query.filter(
        func.date(Booking.booking_date) >= start_date,
        func.date(Booking.booking_date) <= end_date
    ).all()

    total_tickets = len(period_bookings)
    confirmed = [b for b in period_bookings if b.booking_status == 'Confirmed']
    cancelled = [b for b in period_bookings if b.booking_status == 'Cancelled']
    total_revenue = sum(float(b.total_amount or 0) for b in confirmed)
    refund_amount = sum(float(b.total_amount or 0) for b in cancelled)

    # Most popular route
    route_counts = {}
    for b in period_bookings:
        if b.schedule and b.schedule.route:
            key = f'{b.schedule.route.origin} → {b.schedule.route.destination}'
            route_counts[key] = route_counts.get(key, 0) + 1
    most_popular = max(route_counts, key=route_counts.get) if route_counts else 'N/A'

    return render_template('admin/reports.html',
                           report_type=report_type,
                           start_date=start_date,
                           end_date=end_date,
                           total_tickets=total_tickets,
                           confirmed_count=len(confirmed),
                           cancelled_count=len(cancelled),
                           total_revenue=total_revenue,
                           refund_amount=refund_amount,
                           most_popular=most_popular)
