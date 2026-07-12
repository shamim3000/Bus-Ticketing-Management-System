import io
import uuid
import qrcode
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas as pdf_canvas


def generate_ticket_number():
    """Generate a unique ticket number like BK-XXXXXXXX."""
    return 'BK-' + uuid.uuid4().hex[:8].upper()


def generate_transaction_id():
    """Generate a unique transaction ID."""
    return 'TXN-' + uuid.uuid4().hex[:10].upper()


def generate_qr_code(data):
    """Generate QR code image bytes for the given data."""
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def generate_ticket_pdf(ticket, booking):
    """Generate a PDF e-ticket and return bytes."""
    buf = io.BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # Header
    c.setFont('Helvetica-Bold', 20)
    c.drawString(1.5 * inch, height - 1 * inch, 'ICT BD Bus Services Ltd')
    c.setFont('Helvetica', 10)
    c.drawString(1.5 * inch, height - 1.3 * inch, 'E-Ticket / Booking Confirmation')

    # Divider
    c.setLineWidth(1)
    c.line(1 * inch, height - 1.5 * inch, width - 1 * inch, height - 1.5 * inch)

    # Ticket info
    schedule = booking.schedule
    route = schedule.route
    bus = schedule.bus
    user = booking.user

    y = height - 2 * inch
    info = [
        ('Ticket Number:', ticket.ticket_number),
        ('Passenger:', user.full_name),
        ('Route:', f'{route.origin} → {route.destination}'),
        ('Bus:', f'{bus.bus_name} ({bus.bus_number})'),
        ('Bus Type:', bus.bus_type),
        ('Departure Date:', str(schedule.departure_date)),
        ('Departure Time:', str(schedule.departure_time)),
        ('Arrival Time:', str(schedule.arrival_time)),
        ('Seat Number:', ticket.seat_number),
        ('Amount Paid:', f'Tk {booking.total_amount}'),
        ('Payment Method:', booking.payment.payment_method if booking.payment else 'N/A'),
        ('Booking Status:', booking.booking_status),
    ]

    c.setFont('Helvetica', 11)
    for label, value in info:
        c.setFont('Helvetica-Bold', 11)
        c.drawString(1.5 * inch, y, label)
        c.setFont('Helvetica', 11)
        c.drawString(3.5 * inch, y, str(value))
        y -= 0.3 * inch

    # QR Code
    qr_data = f'Ticket:{ticket.ticket_number}|Seat:{ticket.seat_number}|Route:{route.origin}-{route.destination}'
    qr_bytes = generate_qr_code(qr_data)
    qr_buf = io.BytesIO(qr_bytes)
    from reportlab.lib.utils import ImageReader
    qr_img = ImageReader(qr_buf)
    c.drawImage(qr_img, 5 * inch, height - 4.5 * inch, width=1.5 * inch, height=1.5 * inch)

    # Footer
    c.setFont('Helvetica-Oblique', 9)
    c.drawString(1.5 * inch, 1 * inch, 'Please present this ticket at the counter. Have a safe journey!')
    c.drawString(1.5 * inch, 0.7 * inch, 'ICT BD Bus Services Ltd - Intercity AC & Non-AC Services')

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


def send_notification(user, subject, message):
    """Simulate sending notification (logs to console)."""
    print(f'[NOTIFICATION] To: {user.email} | Subject: {subject} | Message: {message}')
