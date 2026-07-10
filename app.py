from datetime import datetime
from flask import Flask, abort, render_template, request, redirect, session, url_for
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
                return redirect(url_for('staff_dashboard'))
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
    total_users = User.query.filter(User.role != 'admin').count()
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

@app.route('/admin_staff/<int:staff_id>/<action>', methods=['POST'])
def staff_request_action(staff_id, action):
    staff = Staff.query.get_or_404(staff_id)
    if action == 'approve':
        staff.status = 'approved'
    elif action == 'reject':
        staff.status = 'blacklisted'
    db.session.commit()
    return redirect(url_for('admin_staff', status='pending'))

@app.route('/add_trek', methods=['GET', 'POST'])
def add_trek():
    trek_id = request.args.get('trek_id')
    trek = None
    
    if trek_id:
        trek = Trek.query.get(trek_id)
    
    if request.method == 'POST':
        trek_id = request.form.get('trek_id')
        trek_name = request.form.get('trek_name')
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
                trek.trek_name = trek_name
                trek.trek_location = location
                trek.trek_difficulty = difficulty
                trek.trek_duration = duration
                trek.trek_description = trek_details
                trek.slots = int(slots) if slots and slots.isdigit() else trek.slots
                trek.status = trek_status or trek.status
                trek.start_date = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else trek.start_date
                trek.end_date = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else trek.end_date
                if responsible_trek_staff:
                    trek.user_id = int(responsible_trek_staff)
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
                slots=int(slots) if slots and slots.isdigit() else 0,
                start_date=datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None,
                end_date=datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None,
                status=trek_status or 'active',
                user_id=int(responsible_trek_staff) if responsible_trek_staff else None
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

@app.route('/admin/users/<int:user_id>/<action>', methods=['POST'])
def admin_user_action(user_id, action):
    if session.get('role') != 'admin':
        abort(403)

    user = User.query.get_or_404(user_id)
    if action == 'approve':
        user.approved = True
        user.blacklisted = False
    elif action == 'blacklist':
        user.blacklisted = True
        user.approved = False
    db.session.commit()
    return redirect(url_for('admin_users'))

def get_staff_dashboard_context():
    current_user_id = session.get('user_id')
    assigned_treks = []

    if current_user_id:
        assigned_treks = Trek.query.filter_by(user_id=current_user_id).all()

    assigned_trek = assigned_treks[0] if assigned_treks else None
    total_treks = len(assigned_treks)
    total_users = User.query.filter_by(role='user').count()
    open_treks = Trek.query.filter_by(status='active', user_id=current_user_id).count() if current_user_id else 0
    participants = []

    if assigned_trek:
        participants = Booking.query.filter_by(trek_id=assigned_trek.trek_id).join(User).all()

    return {
        'total_treks': total_treks,
        'total_users': total_users,
        'open_treks': open_treks,
        'assigned_treks': assigned_treks,
        'assigned_trek': assigned_trek,
        'participants': participants
    }

@app.route('/admin_bookings')
def admin_bookings():
    if session.get('role') != 'admin':
        abort(403)

    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/admin_booking.html', bookings=bookings)

@app.route('/staff_dash')
def staff_dashboard():
    context = get_staff_dashboard_context()
    return render_template('staff/staff_dash.html', **context)

@app.route('/staff_trek')
def staff_trek():
    context = get_staff_dashboard_context()
    return render_template('staff/staff_trek.html', **context)

@app.route('/staff_user')
def staff_user():
    trek_id = request.args.get('trek_id', type=int)
    context = get_staff_dashboard_context()
    trek = None

    if trek_id:
        trek = Trek.query.get(trek_id)
        if trek:
            context['participants'] = Booking.query.filter_by(trek_id=trek_id).join(User).all()

    return render_template('staff/staff_user.html', trek=trek, **context)

@app.route('/trek_staff_dashboard')
def trek_staff_dashboard():
    return redirect(url_for('staff_dashboard'))

@app.route('/staff_manage')
def staff_manage():
    context = get_staff_dashboard_context()
    return render_template('staff/staff_dash.html', **context)

@app.route('/user_dash')
@app.route('/user_dashboard')
def user_dashboard():
    treks = Trek.query.all()
    user_id = session.get('user_id')
    user_bookings = []
    if user_id:
        user_bookings = Booking.query.filter_by(user_id=user_id).join(Trek).all()

    available_treks = []
    for trek in treks:
        total_booked = Booking.query.filter_by(trek_id=trek.trek_id).count()
        available_treks.append({
            'trek': trek,
            'available_slots': max((trek.slots or 0) - total_booked, 0),
            'booked_by_user': user_id and Booking.query.filter_by(user_id=user_id, trek_id=trek.trek_id).first() is not None
        })

    return render_template(
        'user/user_dash.html',
        user_email=session.get('user_email', 'Guest'),
        user_name=session.get('user_name'),
        available_treks=available_treks,
        bookings=user_bookings
    )

@app.route('/book_trek/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    existing_booking = Booking.query.filter_by(user_id=user_id, trek_id=trek_id).first()
    if not existing_booking:
        booking = Booking(user_id=user_id, trek_id=trek_id, status='booked')
        db.session.add(booking)
        db.session.commit()

    return redirect(url_for('user_dashboard'))

@app.route('/user_booking/<int:booking_id>')
def user_booking(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).join(Trek).first()
    if booking is None:
        return redirect(url_for('user_dashboard'))

    return render_template('user/user_booking.html', booking=booking)

@app.route('/user_treks')
def user_treks():
    treks = Trek.query.all()
    user_id = session.get('user_id')
    available_treks = []
    for trek in treks:
        total_booked = Booking.query.filter_by(trek_id=trek.trek_id).count()
        available_treks.append({
            'trek': trek,
            'available_slots': max((trek.slots or 0) - total_booked, 0),
            'booked_by_user': user_id and Booking.query.filter_by(user_id=user_id, trek_id=trek.trek_id).first() is not None
        })
    return render_template('user/user_treks.html', available_treks=available_treks)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__': 
    app.run(debug=True)