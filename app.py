from flask import Flask, abort, render_template, request, redirect, session
from model import * 

app = Flask(__name__) 
app.secret_key = 'your_secret_key'  # Replace with a real secret key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking_mgmnt.db' 

db.init_app(app) 

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    if admin is None:
        admin = User(user_email='admin@gmail.com', 
                     user_name='Admin', 
                     user_password='admin123', 
                     role='admin')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('user_email')
        password = request.form.get('user_password')
        user = User.query.filter_by(user_email=email, user_password=password).first()
        if user is not None:
            session['user_id'] = user.user_id
            session['user_email'] = user.user_email
            session['role'] = user.role
            if user.role == 'admin':
                return redirect('/admin_dash') 
            if user.role == 'trek_staff':
                return redirect('/trek_staff_dashboard')
            if user.role == 'user':
                return redirect('/user_dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('user_email')
        name = request.form.get('user_name')
        password = request.form.get('user_password')
        role = request.form.get('role')
        new_user = User(user_email=email, user_name=name, user_password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/admin_dash')
def admin_dash():
    total_treks = Trek.query.count()
    total_users = User.query.count()
    total_staff = User.query.filter_by(role='trek_staff').count()
    total_bookings = Booking.query.count()
    bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(10).all()
    stats = {
        'total_treks': total_treks,
        'total_users': total_users,
        'total_staff': total_staff,
        'total_bookings': total_bookings
    }
    return render_template('admin/admin_dash.html', stats=stats, bookings=bookings)

@app.route('/admin_manage_trek')
def admin_manage_trek():
    treks = Trek.query.all()
    return render_template('admin/admin_manage_trek.html', treks=treks)

@app.route('/admin_staff')
def admin_staff():
    status = request.args.get('status', 'pending')
    staff_requests = Staff.query.filter_by(status=status).all()
    pending_count = Staff.query.filter_by(status='pending').count()
    approved_count = Staff.query.filter_by(status='approved').count()
    blacklisted_count = Staff.query.filter_by(status='blacklisted').count()
    return render_template(
        'admin/admin_staff.html',
        staff_requests=staff_requests,
        active_status=status,
        pending_count=pending_count,
        approved_count=approved_count,
        blacklisted_count=blacklisted_count
    )

@app.route('/add_trek', methods=['GET', 'POST'])
def add_trek():
    trek_id = request.args.get('trek_id')
    trek = None
    
    if trek_id:
        trek = Trek.query.get(trek_id)
    
    if request.method == 'POST':
        trek_id = request.form.get('trek_id')
        trek_name = request.form.get('trek_name')
        trek_name_upd = request.form.get('trek_name_upd')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration = request.form.get('duration')
        slots = request.form.get('slots')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        responsible_trek_staff = request.form.get('responsible_trek_staff')
        trek_status = request.form.get('trek_status')
        trek_details = request.form.get('trek_details')
        
        if trek_id:
            # Update existing trek
            trek = Trek.query.get(trek_id)
            if trek:
                trek.trek_name = trek_name_upd or trek_name
                trek.trek_location = location
                trek.trek_difficulty = difficulty
                trek.trek_duration = duration
                trek.trek_description = trek_details
                if responsible_trek_staff:
                    trek.user_id = responsible_trek_staff
                db.session.commit()
                return redirect('/admin_manage_trek')
        else:
            # Create new trek
            new_trek = Trek(
                trek_name=trek_name,
                trek_location=location,
                trek_difficulty=difficulty,
                trek_duration=duration,
                trek_description=trek_details,
                user_id=responsible_trek_staff if responsible_trek_staff else None
            )
            db.session.add(new_trek)
            db.session.commit()
            return redirect('/admin_manage_trek')
    
    staff = User.query.filter_by(role='trek_staff').all()
    return render_template('admin/add_treks.html', trek=trek, staff=staff)

@app.route('/add_trek/<int:trek_id>', methods=['DELETE', 'POST'])
def delete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if trek:
        db.session.delete(trek)
        db.session.commit()
    return redirect('/admin_manage_trek')

@app.route('/admin/users', endpoint='admin_users')
def list_users():
    # Ensure only admins can access this page
    if session.get('role') != 'admin':
        abort(403)
        
    # Fetch all users from the database
    users = User.query.all()
    return render_template('admin/admin_user.html', users=users)

if __name__ == '__main__': 
    app.run(debug=True)