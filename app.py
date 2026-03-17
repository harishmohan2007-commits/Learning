from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
 
app = Flask(__name__, static_folder='.')
app.config['SECRET_KEY'] = 'antigravity-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///antigravity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
 
db = SQLAlchemy(app)
login_manager = LoginManager(app)
 
# ── MODELS ──────────────────────────────────────────
 
class User(UserMixin, db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    phone      = db.Column(db.String(20), nullable=True)
    password   = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 
    def set_password(self, password):
        self.password = generate_password_hash(password)
 
    def check_password(self, password):
        return check_password_hash(self.password, password)
 
 
class Booking(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name  = db.Column(db.String(50), nullable=False)
    email      = db.Column(db.String(120), nullable=False)
    phone      = db.Column(db.String(20), nullable=False)
    event      = db.Column(db.String(100), nullable=False)
    date       = db.Column(db.String(20), nullable=False)
    time       = db.Column(db.String(20), nullable=False)
    level      = db.Column(db.String(50), nullable=False)
    notes      = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
 
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
 
 
# ── SERVE HTML PAGES ─────────────────────────────────
 
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')
 
@app.route('/booking')
def booking():
    return send_from_directory('.', 'booking.html')
 
@app.route('/login')
def login_page():
    return send_from_directory('.', 'login.html')
 
 
# ── BOOKING API ──────────────────────────────────────
 
@app.route('/api/book', methods=['POST'])
def book():
    data = request.get_json()
 
    booking = Booking(
        first_name = data.get('firstName', ''),
        last_name  = data.get('lastName', ''),
        email      = data.get('email', ''),
        phone      = data.get('phone', ''),
        event      = data.get('event', ''),
        date       = data.get('date', ''),
        time       = data.get('time', ''),
        level      = data.get('level', ''),
        notes      = data.get('notes', '')
    )
    db.session.add(booking)
    db.session.commit()
 
    return jsonify({'success': True, 'message': 'Booking confirmed!'})
 
 
# ── AUTH API ─────────────────────────────────────────
 
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
 
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'message': 'Email already registered.'})
 
    user = User(
        first_name = data['firstName'],
        last_name  = data['lastName'],
        email      = data['email'],
        phone      = data.get('phone', '')
    )
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
 
    login_user(user)
    return jsonify({'success': True, 'message': 'Account created!'})
 
 
@app.route('/api/login', methods=['POST'])
def login():
    data  = request.get_json()
    user  = User.query.filter_by(email=data['email']).first()
 
    if user and user.check_password(data['password']):
        login_user(user)
        return jsonify({'success': True, 'message': 'Logged in!'})
 
    return jsonify({'success': False, 'message': 'Invalid email or password.'})
 
 
@app.route('/api/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out.'})
 
 
# ── RUN ──────────────────────────────────────────────
 
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
