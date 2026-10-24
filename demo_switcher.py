"""
Add patient switcher API endpoint for demo mode
"""
from flask import jsonify

def add_demo_switcher_route(app):
    @app.route('/api/demo/switch/<int:patient_id>', methods=['POST'])
    def switch_patient(patient_id):
        """Switch to a different demo patient"""
        from flask import session
        import database
        
        # Get patient
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
            'message': f'Switched to {patient["name"]}',
            'patient': patient
        })
