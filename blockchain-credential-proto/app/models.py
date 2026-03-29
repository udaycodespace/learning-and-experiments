import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from pathlib import Path

# FIXED: Import DATA_DIR from project root for database path [web:72]
try:
    from core import DATA_DIR, PROJECT_ROOT  # Import from sibling package
except ImportError:
    # Fallback for direct imports
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication with role-based access"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # issuer, student, verifier
    student_id = db.Column(db.String(50), unique=True, nullable=True)  # For students
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


def init_database(app):
    """Initialize database with app context and proper data/ path"""
    # FIXED: Ensure DATA_DIR exists before DB creation
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # Create default admin/issuer account if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                role='issuer',
                full_name='System Administrator',
                email='admin@gprec.ac.in'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create a sample issuer account
            issuer = User(
                username='issuer1',
                role='issuer',
                full_name='Dr. Academic Dean',
                email='dean@gprec.ac.in'
            )
            issuer.set_password('issuer123')
            db.session.add(issuer)
            
            # Create sample student account
            student = User(
                username='Sample Student',
                role='student',
                student_id='SAMPLE001',
                full_name='Sample Student',
                email='student@gprec.ac.in'
            )
            student.set_password('SAMPLE001')
            db.session.add(student)
            
            # Create sample verifier account
            verifier = User(
                username='verifier1',
                role='verifier',
                full_name='HR Manager',
                email='hr@company.com'
            )
            verifier.set_password('verifier123')
            db.session.add(verifier)
            
            db.session.commit()
            print("Default users created successfully!")
            print(f"Database file: {DATA_DIR / 'credentials.db'}")
