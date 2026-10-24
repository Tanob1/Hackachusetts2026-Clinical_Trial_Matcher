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
    print("🚀 Clinical Trial Matcher API Server")
    print("="*50)
    print("\n🌐 Web App: http://localhost:5000")
    print("📚 API Documentation: See API_DOCUMENTATION.md")
    print("🧪 Sample user: sarah.chen / demo123")
    print("\n💡 Quick test:")
    print('   curl -X POST http://localhost:5000/login \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"username":"sarah.chen","password":"demo123"}\'')
    print("\n" + "="*50 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
