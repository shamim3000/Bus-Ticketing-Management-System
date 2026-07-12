from app.extensions import db


class Bus(db.Model):
    __tablename__ = 'buses'

    bus_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_number = db.Column(db.String(20), unique=True)
    bus_name = db.Column(db.String(100))
    bus_type = db.Column(db.Enum('AC', 'Non-AC', name='bus_type_enum'))
    total_seats = db.Column(db.Integer)
    registration_number = db.Column(db.String(50), unique=True)
    status = db.Column(db.Enum('Available', 'Maintenance', 'Inactive', name='bus_status_enum'), default='Available')

    schedules = db.relationship('Schedule', backref='bus', lazy=True)

    def __repr__(self):
        return f'<Bus {self.bus_number}>'
