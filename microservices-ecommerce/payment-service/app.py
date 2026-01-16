from flask import Flask, jsonify, request
from datetime import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

# Configuración de base de datos
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/paymentdb')

def get_db_connection():
    """Conexión a PostgreSQL"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    """Inicializar tabla de pagos"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    amount DECIMAL(10, 2) NOT NULL,
                    currency VARCHAR(3) DEFAULT 'COP',
                    status VARCHAR(20) DEFAULT 'pending',
                    payment_method VARCHAR(50),
                    transaction_id VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("✅ Payment table initialized successfully")
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
        'service': 'payment-service',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint detallado"""
    conn = get_db_connection()
    payment_count = 0
    total_amount = 0
    
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM payments')
            result = cur.fetchone()
            payment_count = result[0]
            total_amount = float(result[1])
            cur.close()
            conn.close()
        except:
            pass
    
    return jsonify({
        'service': 'payment-service',
        'status': 'operational',
        'database': 'PostgreSQL',
        'total_payments': payment_count,
        'total_amount': total_amount,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/payments', methods=['GET'])
def get_payments():
    """Obtener todos los pagos"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM payments ORDER BY id DESC')
        payments = cur.fetchall()
        cur.close()
        conn.close()
        
        # Convertir Decimal a float para JSON
        for payment in payments:
            payment['amount'] = float(payment['amount'])
        
        return jsonify({
            'success': True,
            'count': len(payments),
            'payments': payments
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payments', methods=['POST'])
def create_payment():
    """Crear nuevo pago"""
    data = request.get_json()
    
    required_fields = ['order_id', 'user_id', 'amount']
    if not data or not all(field in data for field in required_fields):
        return jsonify({
            'error': 'Missing required fields: order_id, user_id, amount'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('''
            INSERT INTO payments 
            (order_id, user_id, amount, payment_method, transaction_id)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        ''', (
            data['order_id'],
            data['user_id'],
            data['amount'],
            data.get('payment_method', 'credit_card'),
            data.get('transaction_id', f"TXN-{datetime.utcnow().timestamp()}")
        ))
        
        new_payment = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        
        # Convertir Decimal a float
        new_payment['amount'] = float(new_payment['amount'])
        
        # TODO: Publicar evento PaymentCreated en RabbitMQ
        
        return jsonify({
            'success': True,
            'message': 'Payment created successfully',
            'payment': new_payment
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payments/<int:payment_id>', methods=['GET'])
def get_payment(payment_id):
    """Obtener pago por ID"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM payments WHERE id = %s', (payment_id,))
        payment = cur.fetchone()
        cur.close()
        conn.close()
        
        if payment:
            payment['amount'] = float(payment['amount'])
            return jsonify({
                'success': True,
                'payment': payment
            }), 200
        else:
            return jsonify({
                'error': 'Payment not found'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payments/<int:payment_id>/status', methods=['PUT'])
def update_payment_status(payment_id):
    """Actualizar estado del pago"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({
            'error': 'Missing required field: status'
        }), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor()
        cur.execute('''
            UPDATE payments 
            SET status = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        ''', (data['status'], payment_id))
        
        conn.commit()
        rows_affected = cur.rowcount
        cur.close()
        conn.close()
        
        if rows_affected > 0:
            return jsonify({
                'success': True,
                'message': 'Payment status updated successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Payment not found'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Información del servicio"""
    return jsonify({
        'service': 'Payment Service',
        'version': '1.0.0',
        'database': 'PostgreSQL',
        'author': 'Alejandro De Mendoza',
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'payments': '/payments [GET, POST]',
            'payment_detail': '/payments/<id> [GET]',
            'update_status': '/payments/<id>/status [PUT]'
        }
    }), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)