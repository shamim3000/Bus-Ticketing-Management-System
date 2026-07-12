from app.extensions import db


class Route(db.Model):
    __tablename__ = 'routes'

    route_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin = db.Column(db.String(100))
    destination = db.Column(db.String(100))
    distance_km = db.Column(db.Numeric(6, 2))
    estimated_duration = db.Column(db.String(30))
    fare = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum('Active', 'Inactive', name='route_status_enum'), default='Active')

    schedules = db.relationship('Schedule', backref='route', lazy=True)

    def __repr__(self):
        return f'<Route {self.origin} -> {self.destination}>'
