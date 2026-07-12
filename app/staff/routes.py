from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request, session, Response
from flask_login import login_required, current_user
from app.staff import staff_bp
from app.auth.decorators import role_required
from app.extensions import db
from app.models.bus import Bus
from app.models.route import Route
from app.models.schedule import Schedule
from app.models.booking import Booking
from app.models.ticket import Ticket
from app.models.payment import Payment
from app.models.user import User
from app.utils.helpers import generate_ticket_number, generate_transaction_id, generate_ticket_pdf, send_notification
from sqlalchemy import func


@staff_bp.before_request
@login_required
@role_required('Staff')
def before_request():
    pass


@staff_bp.route('/dashboard')
def dashboard():
    today = date.today()
    today_sales = Booking.query.filter(
        func.date(Booking.booking_date) == today
    ).count()
    today_revenue = db.session.query(
        func.coalesce(func.sum(Payment.payment_amount), 0)
    ).filter(
        Payment.payment_status == 'Paid',
        func.date(Payment.payment_date) == today
    ).scalar()
    confirmed_today = Booking.query.filter(
        func.date(Booking.booking_date) == today,
        Booking.booking_status == 'Confirmed'
    ).count()
    pending_today = Booking.query.filter(
        func.date(Booking.booking_date) == today,
        Booking.booking_status == 'Pending'
    ).count()

    recent = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()

    return render_template('staff/dashboard.html',
                           today_sales=today_sales,
                           today_revenue=today_revenue,
                           confirmed_today=confirmed_today,
                           pending_today=pending_today,
                           recent=recent)


@staff_bp.route('/book-ticket', methods=['GET', 'POST'])
def book_ticket():
    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        travel_date = request.form.get('travel_date')
        travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date() if travel_date else None

        results = Schedule.query.join(Route).join(Bus).filter(
            Route.origin == origin,
            Route.destination == destination,
            Schedule.departure_date == travel_date_obj,
            Schedule.status == 'Scheduled',
            Schedule.available_seats > 0
        ).all()

        cities = ['Dhaka', 'Khulna', 'Rajshahi', 'Sylhet']
        return render_template('staff/book_ticket.html',
                               results=results, cities=cities,
                               origin=origin, destination=destination,
                               travel_date=travel_date)

    cities = ['Dhaka', 'Khulna', 'Rajshahi', 'Sylhet']
    return render_template('staff/book_ticket.html', results=None, cities=cities)


@staff_bp.route('/select-seat/<int:schedule_id>')
def select_seat(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule or schedule.status != 'Scheduled':
        flash('Schedule not available.', 'danger')
        return redirect(url_for('staff.book_ticket'))

    booked_seats = db.session.query(Ticket.seat_number).join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.booking_status.in_(['Confirmed', 'Pending']),
        Ticket.ticket_status != 'Cancelled'
    ).all()
    booked_list = [s[0] for s in booked_seats]

    bus = schedule.bus
    total = bus.total_seats
    rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    cols = [1, 2, 3, 4]
    seats = []
    count = 0
    for row in rows:
        for col in cols:
            if count >= total:
                break
            seat_label = f'{row}{col}'
            seats.append({'label': seat_label, 'booked': seat_label in booked_list})
            count += 1
        if count >= total:
            break

    route = schedule.route
    return render_template('staff/select_seat.html',
                           schedule=schedule, seats=seats,
                           bus=bus, route=route, fare=route.fare)


@staff_bp.route('/confirm-booking/<int:schedule_id>', methods=['POST'])
def confirm_booking(schedule_id):
    seat_number = request.form.get('seat_number')
    passenger_name = request.form.get('passenger_name')
    passenger_phone = request.form.get('passenger_phone')
    payment_method = request.form.get('payment_method')

    if not seat_number:
        flash('Please select a seat.', 'danger')
        return redirect(url_for('staff.select_seat', schedule_id=schedule_id))

    schedule = db.session.get(Schedule, schedule_id)
    if not schedule or schedule.available_seats <= 0:
        flash('No seats available.', 'danger')
        return redirect(url_for('staff.book_ticket'))

    # Check seat
    existing = db.session.query(Ticket).join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Ticket.seat_number == seat_number,
        Booking.booking_status.in_(['Confirmed', 'Pending']),
        Ticket.ticket_status != 'Cancelled'
    ).first()
    if existing:
        flash('Seat already booked.', 'danger')
        return redirect(url_for('staff.select_seat', schedule_id=schedule_id))

    # Find or create passenger user
    user = User.query.filter_by(phone=passenger_phone).first()
    if not user:
        user = User(
            full_name=passenger_name or 'Walk-in Passenger',
            email=f'walkin_{passenger_phone or "na"}@placeholder.com',
            phone=passenger_phone or 'N/A',
            role='Customer',
            status='Active',
        )
        user.set_password('placeholder123')
        db.session.add(user)
        db.session.flush()

    fare = float(schedule.route.fare)

    booking = Booking(
        user_id=user.user_id,
        schedule_id=schedule_id,
        total_amount=fare,
        booking_status='Confirmed',
    )
    db.session.add(booking)
    db.session.flush()

    ticket = Ticket(
        booking_id=booking.booking_id,
        ticket_number=generate_ticket_number(),
        seat_number=seat_number,
        qr_code=str(booking.booking_id),
        ticket_status='Valid',
    )
    db.session.add(ticket)

    payment = Payment(
        booking_id=booking.booking_id,
        payment_method=payment_method or 'Cash',
        transaction_id=generate_transaction_id(),
        payment_amount=fare,
        payment_status='Paid',
    )
    db.session.add(payment)

    schedule.available_seats -= 1
    db.session.commit()

    flash(f'Ticket {ticket.ticket_number} booked for {passenger_name} (Seat {seat_number}).', 'success')
    return redirect(url_for('staff.bookings'))


@staff_bp.route('/bookings')
def bookings():
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('staff/bookings.html', bookings=all_bookings)


@staff_bp.route('/payments')
def payments():
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('staff/payments.html', payments=all_payments)


@staff_bp.route('/reprint/<int:booking_id>')
def reprint_ticket(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or not booking.ticket:
        flash('Ticket not found.', 'danger')
        return redirect(url_for('staff.bookings'))

    pdf_bytes = generate_ticket_pdf(booking.ticket, booking)
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename=ticket_{booking.ticket.ticket_number}.pdf'}
    )


@staff_bp.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        flash('Booking not found.', 'danger')
        return redirect(url_for('staff.bookings'))

    if booking.booking_status == 'Cancelled':
        flash('Already cancelled.', 'info')
        return redirect(url_for('staff.bookings'))

    booking.booking_status = 'Cancelled'
    if booking.ticket:
        booking.ticket.ticket_status = 'Cancelled'
    if booking.schedule:
        booking.schedule.available_seats += 1
    if booking.payment and booking.payment.payment_status == 'Paid':
        refund_amount = float(booking.total_amount) * 0.8
        booking.payment.payment_status = 'Refunded'
        flash(f'Cancelled. Refund Tk {refund_amount:.0f} (80% policy).', 'info')
    else:
        flash('Booking cancelled.', 'info')

    db.session.commit()
    return redirect(url_for('staff.bookings'))
