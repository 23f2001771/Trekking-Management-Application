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

    bookings = db.relationship("Booking", back_populates="user", lazy=True)
    assigned_treks = db.relationship("Trek", back_populates="user", lazy=True) 


class Trek(db.Model): 
    __tablename__ = 'treks'
    trek_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    trek_name = db.Column(db.String(100), nullable=False)
    trek_location = db.Column(db.String(100), nullable=False)
    trek_duration = db.Column(db.String(50), nullable=False)
    trek_difficulty = db.Column(db.String(50), nullable=False)
    trek_description = db.Column(db.String(500))
    bookings = db.relationship("Booking", back_populates="trek", lazy=True)
    user = db.relationship("User", back_populates="assigned_treks", lazy=True)
    

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.trek_id'), nullable=False)
    user = db.relationship("User", back_populates="bookings")
    trek = db.relationship("Trek", back_populates="bookings")
