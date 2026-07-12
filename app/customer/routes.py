import json
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request, jsonify, session, Response
from flask_login import login_required, current_user
from app.customer import customer_bp
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


@customer_bp.before_request
@login_required
@role_required('Customer')
def before_request():
    pass


@customer_bp.route('/search', methods=['GET', 'POST'])
def search_bus():
    if request.method == 'POST':
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        travel_date = request.form.get('travel_date')
        bus_type = request.form.get('bus_type', '')

        # Parse string to date object for PostgreSQL
        travel_date_obj = datetime.strptime(travel_date, '%Y-%m-%d').date() if travel_date else None

        query = Schedule.query.join(Route).join(Bus).filter(
            Route.origin == origin,
            Route.destination == destination,
            Schedule.departure_date == travel_date_obj,
            Schedule.status == 'Scheduled',
            Schedule.available_seats > 0
        )
        if bus_type:
            query = query.filter(Bus.bus_type == bus_type)

        results = query.all()
        # Get unique cities for dropdowns
        cities = ['Dhaka', 'Khulna', 'Rajshahi', 'Sylhet']
        return render_template('customer/search.html',
                               results=results, cities=cities,
                               origin=origin, destination=destination,
                               travel_date=travel_date, bus_type=bus_type)

    cities = ['Dhaka', 'Khulna', 'Rajshahi', 'Sylhet']
    return render_template('customer/search.html', results=None, cities=cities)


@customer_bp.route('/seats/<int:schedule_id>')
def seat_selection(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule or schedule.status != 'Scheduled':
        flash('Schedule not available.', 'danger')
        return redirect(url_for('customer.search_bus'))

    # Get booked seats
    booked_seats = db.session.query(Ticket.seat_number).join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.booking_status.in_(['Confirmed', 'Pending']),
        Ticket.ticket_status != 'Cancelled'
    ).all()
    booked_list = [s[0] for s in booked_seats]

    # Generate seat layout
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
            seats.append({
                'label': seat_label,
                'booked': seat_label in booked_list
            })
            count += 1
        if count >= total:
            break

    route = schedule.route
    return render_template('customer/seat_selection.html',
                           schedule=schedule, seats=seats,
                           bus=bus, route=route, fare=route.fare)


@customer_bp.route('/book/<int:schedule_id>', methods=['POST'])
def book_ticket(schedule_id):
    seat_number = request.form.get('seat_number')
    if not seat_number:
        flash('Please select a seat.', 'danger')
        return redirect(url_for('customer.seat_selection', schedule_id=schedule_id))

    schedule = db.session.get(Schedule, schedule_id)
    if not schedule or schedule.available_seats <= 0:
        flash('No seats available.', 'danger')
        return redirect(url_for('customer.search_bus'))

    # Check if seat already booked
    existing = db.session.query(Ticket).join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Ticket.seat_number == seat_number,
        Booking.booking_status.in_(['Confirmed', 'Pending']),
        Ticket.ticket_status != 'Cancelled'
    ).first()
    if existing:
        flash('Seat already booked. Please choose another.', 'danger')
        return redirect(url_for('customer.seat_selection', schedule_id=schedule_id))

    fare = float(schedule.route.fare)

    # Create booking
    booking = Booking(
        user_id=current_user.user_id,
        schedule_id=schedule_id,
        total_amount=fare,
        booking_status='Pending',
    )
    db.session.add(booking)
    db.session.flush()

    # Create ticket
    ticket = Ticket(
        booking_id=booking.booking_id,
        ticket_number=generate_ticket_number(),
        seat_number=seat_number,
        qr_code=booking.booking_id,
        ticket_status='Valid',
    )
    db.session.add(ticket)

    # Update available seats
    schedule.available_seats -= 1

    # Store in session for payment
    session['pending_booking_id'] = booking.booking_id

    db.session.commit()
    return redirect(url_for('customer.payment'))


@customer_bp.route('/payment', methods=['GET', 'POST'])
def payment():
    booking_id = session.get('pending_booking_id')
    if not booking_id:
        flash('No pending booking.', 'warning')
        return redirect(url_for('customer.search_bus'))

    booking = db.session.get(Booking, booking_id)
    if not booking or booking.booking_status != 'Pending':
        flash('Invalid booking.', 'danger')
        return redirect(url_for('customer.search_bus'))

    if request.method == 'POST':
        method = request.form.get('payment_method')
        if not method:
            flash('Select a payment method.', 'danger')
            return render_template('customer/payment.html', booking=booking)

        payment = Payment(
            booking_id=booking.booking_id,
            payment_method=method,
            transaction_id=generate_transaction_id(),
            payment_amount=booking.total_amount,
            payment_status='Paid',
        )
        booking.booking_status = 'Confirmed'
        db.session.add(payment)
        db.session.commit()

        # Clear session
        session.pop('pending_booking_id', None)

        # Send notification
        send_notification(current_user, 'Booking Confirmed',
                          f'Your ticket {booking.ticket.ticket_number} has been confirmed.')

        flash('Payment successful! Your ticket has been confirmed.', 'success')
        return redirect(url_for('customer.booking_history'))

    return render_template('customer/payment.html', booking=booking)


@customer_bp.route('/history')
def booking_history():
    bookings = Booking.query.filter_by(user_id=current_user.user_id).order_by(Booking.booking_date.desc()).all()
    return render_template('customer/history.html', bookings=bookings)


@customer_bp.route('/download-ticket/<int:booking_id>')
def download_ticket(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or (booking.user_id != current_user.user_id):
        flash('Access denied.', 'danger')
        return redirect(url_for('customer.booking_history'))

    if not booking.ticket:
        flash('No ticket found.', 'danger')
        return redirect(url_for('customer.booking_history'))

    pdf_bytes = generate_ticket_pdf(booking.ticket, booking)
    return Response(
        pdf_bytes,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment;filename=ticket_{booking.ticket.ticket_number}.pdf'}
    )


@customer_bp.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    if not booking or booking.user_id != current_user.user_id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customer.booking_history'))

    if booking.booking_status == 'Cancelled':
        flash('Already cancelled.', 'info')
        return redirect(url_for('customer.booking_history'))

    # Cancel booking
    booking.booking_status = 'Cancelled'
    if booking.ticket:
        booking.ticket.ticket_status = 'Cancelled'

    # Restore seat
    if booking.schedule:
        booking.schedule.available_seats += 1

    # Process refund
    if booking.payment and booking.payment.payment_status == 'Paid':
        # 80% refund policy
        refund_amount = float(booking.total_amount) * 0.8
        booking.payment.payment_status = 'Refunded'
        flash(f'Booking cancelled. Refund of Tk {refund_amount:.0f} will be processed (80% policy).', 'info')
    else:
        flash('Booking cancelled.', 'info')

    db.session.commit()
    send_notification(current_user, 'Booking Cancelled',
                      f'Your booking #{booking.booking_id} has been cancelled.')
    return redirect(url_for('customer.booking_history'))


@customer_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.address = request.form.get('address', current_user.address)
        new_password = request.form.get('new_password')
        if new_password and len(new_password) >= 6:
            current_user.set_password(new_password)
        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('customer.profile'))

    return render_template('customer/profile.html')


# AJAX endpoint for seat availability
@customer_bp.route('/api/seats/<int:schedule_id>')
def api_seat_availability(schedule_id):
    schedule = db.session.get(Schedule, schedule_id)
    if not schedule:
        return jsonify({'error': 'Not found'}), 404

    booked_seats = db.session.query(Ticket.seat_number).join(Booking).filter(
        Booking.schedule_id == schedule_id,
        Booking.booking_status.in_(['Confirmed', 'Pending']),
        Ticket.ticket_status != 'Cancelled'
    ).all()

    return jsonify({
        'available_seats': schedule.available_seats,
        'booked_seats': [s[0] for s in booked_seats]
    })
