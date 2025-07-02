# app.py

from flask import Flask, render_template, request, jsonify, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt

# --- App & DB Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cla-very-secret-and-secure-key-for-sessions'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yearbook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = None

# Handle API auth failure
@login_manager.unauthorized_handler
def unauthorized():
    return make_response(jsonify({'success': False, 'message': 'Login required'}), 401)

# --- Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'graduated' or 'current'
    batch_year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(20), nullable=False)
    section = db.Column(db.String(10), nullable=False)
    is_best_outgoing = db.Column(db.Boolean, default=False)
    is_branch_topper = db.Column(db.Boolean, default=False)
    personal_quote = db.Column(db.String(300))
    linkedin_url = db.Column(db.String(200))
    instagram_handle = db.Column(db.String(100))
    phone_number = db.Column(db.String(20))
    is_new = db.Column(db.Boolean, default=True)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'roll_number': self.roll_number,
            'name': self.name,
            'email': self.email,
            'user_type': self.user_type,
            'batch_year': self.batch_year,
            'branch': self.branch,
            'section': self.section,
            'personal_quote': self.personal_quote,
            'linkedin_url': self.linkedin_url,
            'instagram_handle': self.instagram_handle,
            'phone_number': self.phone_number,
            'is_best_outgoing': self.is_best_outgoing,
            'is_branch_topper': self.is_branch_topper
        }

from flask_login import UserMixin
class User(UserMixin, User):
    pass

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

# --- Authentication ---
@app.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()
    if not data or not data.get('roll_number') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Missing credentials'}), 400

    user = User.query.filter_by(roll_number=data['roll_number']).first()
    if user and user.check_password(data['password']):
        login_user(user)
        if user.is_new:
            session['show_guide'] = True
            user.is_new = False
            db.session.commit()
        return jsonify({'success': True, 'message': 'Login successful!', 'user': user.to_dict()})

    return jsonify({'success': False, 'message': 'Invalid roll number or password'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout_api():
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/api/status')
def status_api():
    if current_user.is_authenticated:
        return jsonify({'logged_in': True, 'user': current_user.to_dict()})
    return jsonify({'logged_in': False})

# --- Data APIs ---
@app.route('/api/batches')
@login_required
def get_batches():
    batches = db.session.query(User.batch_year).filter_by(user_type='graduated').distinct().order_by(User.batch_year.desc()).all()
    return jsonify([b[0] for b in batches])

@app.route('/api/batch/<int:year>')
@login_required
def get_batch_details(year):
    best_student = User.query.filter_by(batch_year=year, is_best_outgoing=True).first()
    branches = db.session.query(User.branch).filter_by(batch_year=year).distinct().all()
    return jsonify({
        'batch_year': year,
        'best_outgoing_student': best_student.to_dict() if best_student else None,
        'branches': [b[0] for b in branches]
    })

@app.route('/api/branch/<int:year>/<string:branch_code>')
@login_required
def get_branch_details(year, branch_code):
    branch_topper = User.query.filter_by(batch_year=year, branch=branch_code, is_branch_topper=True).first()
    sections = db.session.query(User.section).filter_by(batch_year=year, branch=branch_code).distinct().all()
    return jsonify({
        'branch_topper': branch_topper.to_dict() if branch_topper else None,
        'sections': [s[0] for s in sections]
    })

@app.route('/api/section/<int:year>/<string:branch_code>/<string:section_code>')
@login_required
def get_section_students(year, branch_code, section_code):
    students = User.query.filter_by(batch_year=year, branch=branch_code, section=section_code).all()
    return jsonify([student.to_dict() for student in students])

@app.route('/api/profile/<string:roll_number>')
@login_required
def get_profile(roll_number):
    user = User.query.filter_by(roll_number=roll_number).first_or_404()
    return jsonify(user.to_dict())

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    if current_user.user_type != 'graduated':
        return jsonify({'success': False, 'message': 'Only graduated students can edit profiles.'}), 403

    data = request.get_json()
    if 'linkedin_url' in data:
        current_user.linkedin_url = data['linkedin_url']
    if 'instagram_handle' in data:
        current_user.instagram_handle = data['instagram_handle']
    if 'phone_number' in data:
        current_user.phone_number = data['phone_number']
    if 'personal_quote' in data:
        current_user.personal_quote = data['personal_quote']

    db.session.commit()
    return jsonify({'success': True, 'message': 'Profile updated successfully!', 'user': current_user.to_dict()})

@app.route('/api/branches')
@login_required
def get_all_branches():
    branches = db.session.query(User.branch).distinct().all()
    return jsonify([b[0] for b in branches])

@app.route('/clear_guide')
def clear_guide():
    session.pop('show_guide', None)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
