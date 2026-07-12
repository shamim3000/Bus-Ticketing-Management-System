from flask_wtf import FlaskForm
from wtforms import (StringField, IntegerField, DecimalField, SelectField,
                     DateField, TimeField, SubmitField)
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class BusForm(FlaskForm):
    bus_number = StringField('Bus Number', validators=[DataRequired(), Length(max=20)])
    bus_name = StringField('Bus Name', validators=[DataRequired(), Length(max=100)])
    bus_type = SelectField('Bus Type', choices=[('AC', 'AC'), ('Non-AC', 'Non-AC')], validators=[DataRequired()])
    total_seats = IntegerField('Total Seats', validators=[DataRequired(), NumberRange(min=10, max=60)])
    registration_number = StringField('Registration Number', validators=[DataRequired(), Length(max=50)])
    status = SelectField('Status', choices=[('Available', 'Available'), ('Maintenance', 'Maintenance'), ('Inactive', 'Inactive')])
    submit = SubmitField('Save')


class RouteForm(FlaskForm):
    origin = SelectField('Origin', choices=[
        ('Dhaka', 'Dhaka'), ('Khulna', 'Khulna'),
        ('Rajshahi', 'Rajshahi'), ('Sylhet', 'Sylhet')
    ], validators=[DataRequired()])
    destination = SelectField('Destination', choices=[
        ('Dhaka', 'Dhaka'), ('Khulna', 'Khulna'),
        ('Rajshahi', 'Rajshahi'), ('Sylhet', 'Sylhet')
    ], validators=[DataRequired()])
    distance_km = DecimalField('Distance (KM)', validators=[DataRequired(), NumberRange(min=1)])
    estimated_duration = StringField('Estimated Duration', validators=[DataRequired(), Length(max=30)])
    fare = DecimalField('Fare (Tk)', validators=[DataRequired(), NumberRange(min=1)])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    submit = SubmitField('Save')


class ScheduleForm(FlaskForm):
    bus_id = SelectField('Select Bus', coerce=int, validators=[DataRequired()])
    route_id = SelectField('Select Route', coerce=int, validators=[DataRequired()])
    departure_date = DateField('Departure Date', validators=[DataRequired()])
    departure_time = TimeField('Departure Time', validators=[DataRequired()])
    arrival_time = TimeField('Arrival Time', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')])
    submit = SubmitField('Save')


class UserForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Length(max=100)])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    role = SelectField('Role', choices=[('Administrator', 'Administrator'), ('Staff', 'Staff'), ('Customer', 'Customer')])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    submit = SubmitField('Save')
