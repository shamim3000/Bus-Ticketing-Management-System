from datetime import datetime
from app.extensions import db


class Booking(db.Model):
    __tablename__ = 'bookings'

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.schedule_id'))
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Numeric(10, 2))
    booking_status = db.Column(
        db.Enum('Pending', 'Confirmed', 'Cancelled', name='booking_status_enum'),
        default='Pending'
    )

    ticket = db.relationship('Ticket', backref='booking', uselist=False, lazy=True)
    payment = db.relationship('Payment', backref='booking', uselist=False, lazy=True)

    def __repr__(self):
        return f'<Booking {self.booking_id}>'
