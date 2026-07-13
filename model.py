from datetime import datetime
from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    user_password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(25), default='user')
    approved = db.Column(db.Boolean, default=False)
    blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = db.relationship('Booking', back_populates='user', lazy=True)
    assigned_treks = db.relationship('Trek', back_populates='user', lazy=True)
    staff_profile = db.relationship('Staff', back_populates='user', uselist=False)

    


class Trek(db.Model):
    __tablename__ = 'treks'
    trek_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    trek_name = db.Column(db.String(100), nullable=False)
    trek_location = db.Column(db.String(100), nullable=False)
    trek_duration = db.Column(db.String(50), nullable=False)
    trek_difficulty = db.Column(db.String(50), nullable=False)
    trek_description = db.Column(db.String(500))
    slots = db.Column(db.Integer, default=0)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    bookings = db.relationship('Booking', back_populates='trek', lazy=True)
    user = db.relationship('User', back_populates='assigned_treks', lazy=True)

    


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.trek_id'), nullable=False)
    booking_date = db.Column(db.DateTime(), default=db.func.now())
    status = db.Column(db.String(50), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')

    


class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    contact = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='staff_profile')
    assignments = db.relationship('StaffAssignment', back_populates='staff', cascade='all, delete-orphan')

    

class StaffAssignment(db.Model):
    __tablename__ = 'staff_assignments'
    assignment_id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.trek_id'), nullable=False)
    assignment_date = db.Column(db.DateTime(), default=db.func.now())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    staff = db.relationship('Staff', back_populates='assignments')
    trek = db.relationship('Trek')

   

