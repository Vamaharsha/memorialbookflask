# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, bcrypt # We will create 'db' and 'bcrypt' in app.py

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    user_type = db.Column(db.String(20), nullable=False, default='current') # 'graduated' or 'current'
    
    # Profile information
    batch_year = db.Column(db.Integer, nullable=False)
    branch = db.Column(db.String(10), nullable=False) # e.g., 'CSE', 'ECE'
    section = db.Column(db.String(5), nullable=False)
    linkedin_url = db.Column(db.String(200), nullable=True)
    instagram_handle = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    personal_quote = db.Column(db.Text, nullable=True)
    cgpa = db.Column(db.Float, nullable=True)
    
    # For honor rolls
    is_best_outgoing = db.Column(db.Boolean, default=False)
    is_branch_topper = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=True)


    def __init__(self, roll_number, name, email, password, user_type, batch_year, branch, section, **kwargs):
        self.roll_number = roll_number
        self.name = name
        self.email = email
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.user_type = user_type
        self.batch_year = batch_year
        self.branch = branch
        self.section = section
        # Set other optional fields
        for key, value in kwargs.items():
            setattr(self, key, value)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Returns a dictionary representation of the user for API responses."""
        return {
            'roll_number': self.roll_number,
            'name': self.name,
            'email': self.email,
            'user_type': self.user_type,
            'batch_year': self.batch_year,
            'branch': self.branch,
            'section': self.section,
            'linkedin_url': self.linkedin_url or "Not added yet",
            'instagram_handle': self.instagram_handle or "Not added yet",
            'phone_number': self.phone_number or "Not added yet",
            'personal_quote': self.personal_quote or "The future belongs to those who believe in the beauty of their dreams.",
            'cgpa': self.cgpa
        }