from datetime import datetime
from app.extensions import db


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.booking_id'), unique=True)
    payment_method = db.Column(
        db.Enum('Cash', 'Card', 'bKash', 'Nagad', 'Rocket', name='payment_method_enum')
    )
    transaction_id = db.Column(db.String(100), unique=True)
    payment_amount = db.Column(db.Numeric(10, 2))
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(
        db.Enum('Pending', 'Paid', 'Failed', 'Refunded', name='payment_status_enum'),
        default='Pending'
    )

    def __repr__(self):
        return f'<Payment {self.payment_id}>'
