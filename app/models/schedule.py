from app.extensions import db


class Schedule(db.Model):
    __tablename__ = 'schedules'

    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.bus_id'))
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'))
    departure_date = db.Column(db.Date)
    departure_time = db.Column(db.Time)
    arrival_time = db.Column(db.Time)
    available_seats = db.Column(db.Integer)
    status = db.Column(
        db.Enum('Scheduled', 'Completed', 'Cancelled', name='schedule_status_enum'),
        default='Scheduled'
    )

    bookings = db.relationship('Booking', backref='schedule', lazy=True)

    def __repr__(self):
        return f'<Schedule {self.schedule_id}>'
