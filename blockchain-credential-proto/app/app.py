import os
import logging

# Optionally load environment variables from a .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.debug('Loaded environment variables from .env')
except Exception:
    logging.debug('python-dotenv not available; skipping .env load')

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, session
from datetime import datetime
import json

# FIXED IMPORTS - Correct package structure
from core.blockchain import SimpleBlockchain          # [web:40]
from core.crypto_utils import CryptoManager          # [web:40]
from core.ipfs_client import IPFSClient              # [web:40]
from core.credential_manager import CredentialManager # [web:40]
from .models import db, User, init_database          # [web:42] Relative (same app/)
from .auth import login_required, role_required      # [web:42] Relative (same app/)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# FIXED: Flask app with ROOT-LEVEL template/static paths
app = Flask(__name__,
            template_folder='../templates',    # Point to project root templates/ [web:72]
            static_folder='../static')         # Point to project root static/ [web:72]
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///credentials.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize components
init_database(app)
blockchain = SimpleBlockchain()
crypto_manager = CryptoManager()
ipfs_client = IPFSClient()
credential_manager = CredentialManager(blockchain, crypto_manager, ipfs_client)

@app.route('/')
def index():
    """Main landing page with role selection"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for all user roles"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['student_id'] = user.student_id
            session['full_name'] = user.full_name
            
            flash(f'Welcome {user.full_name or user.username}!', 'success')
            
            if user.role == 'issuer':
                return redirect(url_for('issuer'))
            elif user.role == 'student':
                return redirect(url_for('holder'))
            elif user.role == 'verifier':
                return redirect(url_for('verifier'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('index'))

@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')

@app.route('/issuer')
@role_required('issuer')
def issuer():
    return render_template('issuer.html')

@app.route('/holder')
@role_required('student')
def holder():
    student_id = session.get('student_id')
    all_credentials = credential_manager.get_all_credentials()
    student_credentials = [cred for cred in all_credentials if cred.get('student_id') == student_id]
    return render_template('holder.html', credentials=student_credentials)

@app.route('/verifier')
def verifier():
    return render_template('verifier.html')

# API endpoints
@app.route('/api/issue_credential', methods=['POST'])
@role_required('issuer')
def api_issue_credential():
    try:
        data = request.get_json()
        
        # Core required fields
        required_fields = ['student_name', 'student_id', 'degree', 'university', 'gpa', 'graduation_year']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # NEW: Extended academic fields with validation
        semester = data.get('semester')
        year = data.get('year')
        class_name = data.get('class_name')
        section = data.get('section')
        backlog_count = data.get('backlog_count', 0)
        backlogs = data.get('backlogs', [])
        conduct = data.get('conduct')
        
        # Validate new fields
        if semester is not None and (not isinstance(semester, int) or semester < 1 or semester > 8):
            return jsonify({'error': 'Semester must be between 1 and 8'}), 400
        
        if backlog_count is not None and (not isinstance(backlog_count, int) or backlog_count < 0):
            return jsonify({'error': 'Backlog count must be 0 or greater'}), 400
        
        if conduct and conduct not in ['poor', 'average', 'good', 'outstanding']:
            return jsonify({'error': 'Conduct must be one of: poor, average, good, outstanding'}), 400
        
        # Build extended transcript data
        transcript_data = {
            'student_name': data['student_name'],
            'student_id': data['student_id'],
            'degree': data['degree'],
            'university': data['university'],
            'gpa': float(data['gpa']),
            'graduation_year': int(data['graduation_year']),
            'courses': data.get('courses', []),
            'issue_date': datetime.now().isoformat(),
            'issuer': 'G. Pulla Reddy Engineering College',
            # NEW: Extended academic fields
            'semester': semester,
            'year': year,
            'class_name': class_name,
            'section': section,
            'backlog_count': backlog_count,
            'backlogs': backlogs,
            'conduct': conduct
        }
        
        logging.info(f"Issuing credential with extended data: semester={semester}, backlogs={len(backlogs)}, conduct={conduct}")
        
        result = credential_manager.issue_credential(transcript_data)
        
        if result['success']:
            try:
                student_name = transcript_data['student_name']
                student_id_val = str(transcript_data['student_id'])
                student_user = User.query.filter_by(student_id=student_id_val).first()
                if student_user:
                    student_user.username = student_name
                    student_user.full_name = student_name
                    student_user.set_password(student_id_val)
                    db.session.commit()
                else:
                    conflict = User.query.filter_by(username=student_name).first()
                    username_to_use = f"{student_name} ({student_id_val})" if conflict else student_name
                    
                    new_student = User(
                        username=username_to_use,
                        role='student',
                        student_id=student_id_val,
                        full_name=student_name,
                        email=None
                    )
                    new_student.set_password(student_id_val)
                    db.session.add(new_student)
                    db.session.commit()
            except Exception as e:
                logging.error(f"Error creating/updating student user: {str(e)}")

            flash('Credential issued successfully with extended academic details!', 'success')
            return jsonify(result)
        else:
            return jsonify({'error': result['error']}), 500
            
    except Exception as e:
        logging.error(f"Error issuing credential: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify_credential', methods=['POST'])
def api_verify_credential():
    try:
        data = request.get_json()
        credential_id = data.get('credential_id')
        if not credential_id:
            return jsonify({'error': 'Credential ID is required'}), 400
        result = credential_manager.verify_credential(credential_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error verifying credential: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/selective_disclosure', methods=['POST'])
def api_selective_disclosure():
    try:
        data = request.get_json()
        credential_id = data.get('credential_id')
        fields = data.get('fields', [])
        if not credential_id:
            return jsonify({'error': 'Credential ID is required'}), 400
        if not fields:
            return jsonify({'error': 'At least one field must be selected'}), 400
        result = credential_manager.selective_disclosure(credential_id, fields)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error in selective disclosure: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/blockchain_status')
def api_blockchain_status():
    try:
        status = {
            'total_blocks': len(blockchain.chain),
            'total_credentials': len(credential_manager.get_all_credentials()),
            'last_block_hash': blockchain.get_latest_block().hash if blockchain.chain else None,
            'ipfs_status': ipfs_client.is_connected()
        }
        return jsonify(status)
    except Exception as e:
        logging.error(f"Error getting blockchain status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/credentials')
@role_required('issuer')
def api_credentials():
    try:
        creds = credential_manager.get_all_credentials()
        return jsonify({'success': True, 'credentials': creds})
    except Exception as e:
        logging.error(f"Error listing credentials: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/delete_credential', methods=['POST'])
@role_required('issuer')
def api_delete_credential():
    try:
        data = request.get_json()
        credential_id = data.get('credential_id')
        if not credential_id:
            return jsonify({'success': False, 'error': 'credential_id is required'}), 400
        result = credential_manager.delete_credential(credential_id)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error deleting credential: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_credential/<credential_id>')
def api_get_credential(credential_id):
    try:
        credential = credential_manager.get_credential(credential_id)
        if credential:
            return jsonify({'success': True, 'credential': credential})
        return jsonify({'error': 'Credential not found'}), 404
    except Exception as e:
        logging.error(f"Error getting credential: {str(e)}")
        return jsonify({'error': str(e)}), 500
