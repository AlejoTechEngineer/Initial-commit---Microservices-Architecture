from flask import Flask, jsonify, request
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuración de base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/userdb')

def get_db_connection():
    """Conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    """Inicializar tabla de usuarios"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ User table initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing database: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    db_status = 'connected'
    conn = get_db_connection()
    if not conn:
        db_status = 'disconnected'
    else:
        conn.close()
    
    return jsonify({
        'status': 'healthy',
        'service': 'user-service',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint detallado"""
    conn = get_db_connection()
    user_count = 0
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*) FROM users')
            user_count = cur.fetchone()[0]
            cur.close()
            conn.close()
        except:
            user_count = 0
    
    return jsonify({
        'service': 'user-service',
        'status': 'operational',
        'database': 'PostgreSQL',
        'total_users': user_count,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/users', methods=['GET'])
def get_users():
    """Obtener todos los usuarios"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM users ORDER BY id')
        users = cur.fetchall()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'count': len(users),
            'users': users
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    """Crear nuevo usuario"""
    data = request.get_json()
    
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({
            'error': 'Missing required fields: name, email'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(
            'INSERT INTO users (name, email) VALUES (%s, %s) RETURNING *',
            (data['name'], data['email'])
        )
        new_user = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'User created successfully',
            'user': new_user
        }), 201
    except psycopg2.IntegrityError:
        return jsonify({
            'error': 'Email already exists'
        }), 409
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener usuario por ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        if user:
            return jsonify({
                'success': True,
                'user': user
            }), 200
        else:
            return jsonify({
                'error': 'User not found'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Información del servicio"""
    return jsonify({
        'service': 'User Service',
        'version': '1.0.0',
        'database': 'PostgreSQL',
        'author': 'Alejandro De Mendoza',
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'users': '/users [GET, POST]',
            'user_detail': '/users/<id> [GET]'
        }
    }), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)