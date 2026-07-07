from flask import Flask, render_template, request, redirect 
from model import * 

app = Flask(__name__) 

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking_mgmnt.db' 

db.init_app(app) 

with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    if admin is None:
        admin = User(user_email='admin@example.com', 
                     user_name='Admin', 
                     user_password='password', 
                     role='admin')
        db.session.add(admin)
        db.session.commit()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(user_email=email, user_password=password).first()
        if user is not None:
            if user.role == 'admin':
                return redirect('/admin_dashboard') 
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
        email = request.form['user_email']
        name = request.form['user_name']
        password = request.form['user_password']
        role = request.form['role']
        new_user = User(user_email=email, user_name=name, user_password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

if __name__ == '__main__': 
    app.run(debug=True)