"""
Clinical Trial Matcher - Flask API Server
Hackathon MVP
"""
from flask import Flask, request, jsonify, session, render_template, redirect, url_for
from functools import wraps
import database

app = Flask(__name__)
app.secret_key = 'hackathon-secret-key-change-in-production'  # Change for production!

# CORS headers for mobile app development
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Web UI authentication decorator
def web_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# ============= Authentication Routes =============

@app.route('/login', methods=['POST'])
def login():
    """Login endpoint"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password required'}), 400
    
    # Get user from database
    user = database.get_user_by_username(username)
    
    if user and database.verify_password(user['password_hash'], password):
        # Set session
        session['user_id'] = user['id']
        session['username'] = user['username']
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user['id'],
                'username': user['username']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

# ============= Patient Profile Routes =============

@app.route('/api/patient/me')
@login_required
def get_my_profile():
    """Get current user's patient profile"""
    patient = database.get_patient_by_user_id(session['user_id'])
    if patient:
        return jsonify(patient)
    else:
        return jsonify({'error': 'Patient profile not found'}), 404

@app.route('/api/patient/<int:patient_id>')
@login_required
def get_patient(patient_id):
    """Get patient by ID"""
    # For MVP, allow viewing any patient (for demo switching)
    # In production, add authorization check
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if patient:
        return jsonify(dict(patient))
    else:
        return jsonify({'error': 'Patient not found'}), 404

@app.route('/api/patient/update-conditions', methods=['POST'])
@login_required
def update_patient_conditions():
    """Update patient's medical conditions"""
    data = request.get_json()
    new_conditions = data.get('conditions', '').strip()
    
    if not new_conditions:
        return jsonify({'success': False, 'error': 'Conditions cannot be empty'}), 400
    
    try:
        # Get current patient
        user_id = session.get('user_id')
        patient = database.get_patient_by_user_id(user_id)
        
        if not patient:
            return jsonify({'success': False, 'error': 'Patient not found'}), 404
        
        # Update conditions in database
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patients 
            SET conditions = ? 
            WHERE user_id = ?
        ''', (new_conditions, user_id))
        conn.commit()
        conn.close()
        
        # Clear matching cache since conditions changed
        import matching
        matching.clear_cache()
        
        return jsonify({
            'success': True,
            'message': 'Conditions updated successfully',
            'conditions': new_conditions
        })
    except Exception as e:
        print(f"Error updating conditions: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500
# ============= Trial Matching Routes =============

@app.route('/api/matches/<int:patient_id>')
@login_required
def get_matches(patient_id):
    """Get matched trials for a patient"""
    import matching
    
    # Get patient
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    conn.close()
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    patient = dict(patient)
    
    # Get filters from query params
    max_distance = int(request.args.get('max_distance', 100))
    phase_filter = request.args.get('phase', None)
    
    # Get matches
    matches = matching.get_matches(patient, max_distance=max_distance, phase_filter=phase_filter)
    
    return jsonify({
        'patient_id': patient['id'],
        'patient_name': patient['name'],
        'total_matches': len(matches),
        'filters': {
            'max_distance': max_distance,
            'phase': phase_filter
        },
        'matches': matches
    })

# ============= Trial Information Routes =============

@app.route('/api/trials/<int:trial_id>')
def get_trial(trial_id):
    """Get trial details by ID"""
    trial = database.get_trial_by_id(trial_id)
    if trial:
        return jsonify(trial)
    else:
        return jsonify({'error': 'Trial not found'}), 404

@app.route('/api/trials/search')
def search_trials():
    """Search trials by keyword"""
    query = request.args.get('q', '').lower()
    limit = int(request.args.get('limit', 20))
    
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    
    conn = database.get_db()
    cursor = conn.cursor()
    
    # Search in title and conditions
    cursor.execute('''
        SELECT * FROM trials 
        WHERE LOWER(title) LIKE ? OR LOWER(conditions) LIKE ?
        LIMIT ?
    ''', (f'%{query}%', f'%{query}%', limit))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'query': query,
        'total_results': len(results),
        'results': results
    })

# ============= Demo Routes =============


@app.route('/api/demo/switch/<int:patient_id>', methods=['POST'])
@login_required
def switch_patient(patient_id):
    """Switch to a different demo patient for demo purposes"""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
    patient = cursor.fetchone()
    
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    
    patient = dict(patient)
    
    # Get user for this patient
    cursor.execute('SELECT * FROM users WHERE id = ?', (patient['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user = dict(user)
    
    # Update session
    session['user_id'] = user['id']
    session['username'] = user['username']
    
    return jsonify({
        'success': True,
        'message': f"Switched to {patient['name']}",
        'patient': patient
    })
@app.route('/api/demo/patients')
def get_demo_patients():
    """Get all sample patients for demo purposes"""
    conn = database.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, age, gender, city, conditions FROM patients')
    patients = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'patients': patients})

# ============= Web UI Routes =============

@app.route('/')
def index():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/dashboard')
@web_login_required
def dashboard():
    """Patient dashboard"""
    return render_template('dashboard.html')


# ============= Provider Portal Routes =============

# Provider authentication decorator
def provider_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'provider_id' not in session:
            return redirect(url_for('provider_login_page'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/provider')
def provider_login_page():
    """Provider login page"""
    if 'provider_id' in session:
        return redirect(url_for('provider_search'))
    return render_template('provider_login.html')

@app.route('/provider/login', methods=['POST'])
def provider_login():
    """Provider login endpoint"""
    data = request.form
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return render_template('provider_login.html', error='Email and password required')
    
    # Get provider from database
    provider = database.get_provider_by_email(email)
    
    if provider and database.verify_password(provider['password_hash'], password):
        # Set provider session
        session['provider_id'] = provider['id']
        session['provider_name'] = provider['name']
        session['provider_email'] = provider['email']
        session['hospital_name'] = provider['hospital_name']
        
        return redirect(url_for('provider_search'))
    else:
        return render_template('provider_login.html', error='Invalid credentials')

@app.route('/provider/logout', methods=['POST', 'GET'])
def provider_logout():
    """Provider logout"""
    # Clear only provider session keys
    session.pop('provider_id', None)
    session.pop('provider_name', None)
    session.pop('provider_email', None)
    session.pop('hospital_name', None)
    return redirect(url_for('provider_login_page'))

@app.route('/provider/search')
@provider_login_required
def provider_search():
    """Provider search page"""
    query = request.args.get('q', '')
    results = []
    
    if query:
        results = database.search_patients(query)
    
    return render_template('provider_search.html', 
                         provider_name=session.get('provider_name'),
                         query=query,
                         results=results)

@app.route('/provider/patient/<int:patient_id>')
@provider_login_required
def provider_patient_view(patient_id):
    """View patient profile and matched trials"""
    import matching
    
    # Get patient
    patient = database.get_patient_by_id(patient_id)
    
    if not patient:
        return "Patient not found", 404
    
    # Get matched trials
    matches = matching.get_matches(patient, max_distance=100)
    
    return render_template('provider_patient.html',
                         provider_name=session.get('provider_name'),
                         patient=patient,
                         matches=matches[:10])  # Top 10 matches

@app.route('/provider/referral/create', methods=['POST'])
@provider_login_required
def create_referral():
    """Create a referral and redirect to QR code"""
    patient_id = int(request.form.get('patient_id'))
    trial_id = int(request.form.get('trial_id'))
    provider_notes = request.form.get('provider_notes', '')
    
    # Generate unique referral code
    referral_code = database.generate_referral_code()
    
    # Create referral
    database.create_referral(
        referral_code=referral_code,
        provider_id=session['provider_id'],
        patient_id=patient_id,
        trial_id=trial_id,
        provider_notes=provider_notes
    )
    
    print(f"✅ Created referral: {referral_code}")
    
    return redirect(url_for('view_referral', code=referral_code))

@app.route('/provider/referral/<code>')
@provider_login_required
def view_referral(code):
    """View referral with QR code"""
    import qrcode
    import io
    import base64
    import json
    from datetime import datetime
    
    # Get referral
    referral = database.get_referral_by_code(code)
    
    if not referral:
        return "Referral not found", 404
    
    # Prepare QR code data
    qr_data = {
        'type': 'trial_referral',
        'referral_code': referral['referral_code'],
        'trial_nct_id': referral['nct_id'],
        'provider_name': referral['provider_name'],
        'hospital': referral['hospital_name'],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color='black', back_color='white')
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return render_template('provider_referral.html',
                         provider_name=session.get('provider_name'),
                         referral=referral,
                         qr_code=img_base64)

# ============= Health Check =============

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '1.0',
        'endpoints': {
            'web': ['GET /', 'GET /dashboard'],
            'auth': ['POST /login', 'POST /logout'],
            'patient': ['GET /api/patient/me', 'GET /api/patient/<id>'],
            'matching': ['GET /api/matches/<patient_id>'],
            'trials': ['GET /api/trials/<id>', 'GET /api/trials/search'],
            'demo': ['GET /api/demo/patients']
        }
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("[START] Clinical Trial Matcher API Server")
    print("="*50)
    print("\n[WEB] Web App: http://localhost:5000")
    print("[DOCS] API Documentation: See API_DOCUMENTATION.md")
    print("[TEST] Sample user: sarah.chen / demo123")
    print("\n[TIP] Quick test:")
    print('   curl -X POST http://localhost:5000/login \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"username":"sarah.chen","password":"demo123"}\'')
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)




