from datetime import datetime
from app.extensions import db


class Ticket(db.Model):
    __tablename__ = 'tickets'

    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), unique=True)
    ticket_number = db.Column(db.String(30), unique=True)
    seat_number = db.Column(db.String(10))
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    qr_code = db.Column(db.String(255))
    ticket_status = db.Column(
        db.Enum('Valid', 'Cancelled', 'Used', name='ticket_status_enum'),
        default='Valid'
    )

    def __repr__(self):
        return f'<Ticket {self.ticket_number}>'
