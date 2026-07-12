"""Seed script to create initial admin user and sample data."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.bus import Bus
from app.models.route import Route
from app.models.schedule import Schedule
from datetime import date, time


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(email='admin@ictbd.com').first():
            admin = User(
                full_name='System Administrator',
                email='admin@ictbd.com',
                phone='01700000001',
                role='Administrator',
                status='Active',
            )
            admin.set_password('admin123')
            db.session.add(admin)

        # Create staff user
        if not User.query.filter_by(email='staff@ictbd.com').first():
            staff = User(
                full_name='Counter Staff',
                email='staff@ictbd.com',
                phone='01700000002',
                role='Staff',
                status='Active',
            )
            staff.set_password('staff123')
            db.session.add(staff)

        # Create sample customer
        if not User.query.filter_by(email='customer@test.com').first():
            customer = User(
                full_name='Test Customer',
                email='customer@test.com',
                phone='01700000003',
                role='Customer',
                status='Active',
            )
            customer.set_password('customer123')
            db.session.add(customer)

        # Sample buses
        if Bus.query.count() == 0:
            buses = [
                Bus(bus_number='DHK-101', bus_name='Express Star', bus_type='AC', total_seats=40, registration_number='REG-001', status='Available'),
                Bus(bus_number='DHK-102', bus_name='Green Line', bus_type='AC', total_seats=36, registration_number='REG-002', status='Available'),
                Bus(bus_number='KHU-201', bus_name='Hanif Enterprise', bus_type='Non-AC', total_seats=44, registration_number='REG-003', status='Available'),
                Bus(bus_number='RAJ-301', bus_name='Shyamoli Transport', bus_type='AC', total_seats=40, registration_number='REG-004', status='Available'),
                Bus(bus_number='SYL-401', bus_name='Ena Transport', bus_type='Non-AC', total_seats=40, registration_number='REG-005', status='Available'),
            ]
            db.session.add_all(buses)

        # Sample routes
        if Route.query.count() == 0:
            routes = [
                Route(origin='Dhaka', destination='Khulna', distance_km=330, estimated_duration='7 hours', fare=1200, status='Active'),
                Route(origin='Dhaka', destination='Rajshahi', distance_km=250, estimated_duration='5 hours', fare=900, status='Active'),
                Route(origin='Dhaka', destination='Sylhet', distance_km=300, estimated_duration='6 hours', fare=1100, status='Active'),
                Route(origin='Khulna', destination='Rajshahi', distance_km=280, estimated_duration='6 hours', fare=1000, status='Active'),
                Route(origin='Rajshahi', destination='Sylhet', distance_km=450, estimated_duration='9 hours', fare=1500, status='Active'),
            ]
            db.session.add_all(routes)

        # Sample schedules (tomorrow)
        if Schedule.query.count() == 0:
            tomorrow = date.today().replace(day=date.today().day + 1 if date.today().day < 28 else 1)
            schedules_data = [
                (1, 1, tomorrow, time(6, 0), time(13, 0)),
                (2, 1, tomorrow, time(8, 0), time(15, 0)),
                (3, 2, tomorrow, time(7, 0), time(12, 0)),
                (4, 3, tomorrow, time(9, 0), time(15, 0)),
                (5, 4, tomorrow, time(20, 0), time(5, 0)),
            ]
            for bus_id, route_id, dep_date, dep_time, arr_time in schedules_data:
                bus = db.session.get(Bus, bus_id)
                s = Schedule(
                    bus_id=bus_id,
                    route_id=route_id,
                    departure_date=dep_date,
                    departure_time=dep_time,
                    arrival_time=arr_time,
                    available_seats=bus.total_seats if bus else 40,
                    status='Scheduled',
                )
                db.session.add(s)

        db.session.commit()
        print('Seed data created successfully!')
        print('Admin: admin@ictbd.com / admin123')
        print('Staff: staff@ictbd.com / staff123')
        print('Customer: customer@test.com / customer123')


if __name__ == '__main__':
    seed()
