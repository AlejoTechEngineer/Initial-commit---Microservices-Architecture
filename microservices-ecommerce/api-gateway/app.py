from flask import Flask, jsonify, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# Configuración de URLs de microservicios
USER_SERVICE = os.getenv('USER_SERVICE_URL', 'http://localhost:5001')
ORDER_SERVICE = os.getenv('ORDER_SERVICE_URL', 'http://localhost:5002')
PAYMENT_SERVICE = os.getenv('PAYMENT_SERVICE_URL', 'http://localhost:5003')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint con información detallada"""
    services_status = {}
    
    # Check User Service
    try:
        response = requests.get(f'{USER_SERVICE}/health', timeout=2)
        services_status['user-service'] = 'online' if response.status_code == 200 else 'degraded'
    except:
        services_status['user-service'] = 'offline'
    
    # Check Order Service
    try:
        response = requests.get(f'{ORDER_SERVICE}/health', timeout=2)
        services_status['order-service'] = 'online' if response.status_code == 200 else 'degraded'
    except:
        services_status['order-service'] = 'offline'
    
    # Check Payment Service
    try:
        response = requests.get(f'{PAYMENT_SERVICE}/health', timeout=2)
        services_status['payment-service'] = 'online' if response.status_code == 200 else 'degraded'
    except:
        services_status['payment-service'] = 'offline'
    
    return jsonify({
        'service': 'api-gateway',
        'status': 'operational',
        'timestamp': datetime.utcnow().isoformat(),
        'services': services_status,
        'version': '1.0.0'
    }), 200

# ========== USER SERVICE ROUTES ==========

@app.route('/api/users', methods=['GET', 'POST'])
def users():
    """Proxy para User Service - Gestión de usuarios"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{USER_SERVICE}/users')
        else:
            response = requests.post(f'{USER_SERVICE}/users', json=request.json)
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'User service unavailable',
            'message': str(e)
        }), 503

@app.route('/api/users/<user_id>', methods=['GET'])
def user_detail(user_id):
    """Obtener detalle de usuario específico"""
    try:
        response = requests.get(f'{USER_SERVICE}/users/{user_id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'User service unavailable',
            'message': str(e)
        }), 503

# ========== ORDER SERVICE ROUTES ==========

@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    """Proxy para Order Service - Gestión de pedidos"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{ORDER_SERVICE}/orders')
        else:
            response = requests.post(f'{ORDER_SERVICE}/orders', json=request.json)
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Order service unavailable',
            'message': str(e)
        }), 503

@app.route('/api/orders/<order_id>', methods=['GET'])
def order_detail(order_id):
    """Obtener detalle de pedido específico"""
    try:
        response = requests.get(f'{ORDER_SERVICE}/orders/{order_id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Order service unavailable',
            'message': str(e)
        }), 503

# ========== PAYMENT SERVICE ROUTES ==========

@app.route('/api/payments', methods=['GET', 'POST'])
def payments():
    """Proxy para Payment Service - Gestión de pagos"""
    try:
        if request.method == 'GET':
            response = requests.get(f'{PAYMENT_SERVICE}/payments')
        else:
            response = requests.post(f'{PAYMENT_SERVICE}/payments', json=request.json)
        
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Payment service unavailable',
            'message': str(e)
        }), 503

@app.route('/api/payments/<payment_id>', methods=['GET'])
def payment_detail(payment_id):
    """Obtener detalle de pago específico"""
    try:
        response = requests.get(f'{PAYMENT_SERVICE}/payments/{payment_id}')
        return jsonify(response.json()), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Payment service unavailable',
            'message': str(e)
        }), 503

# ========== ROOT ENDPOINT ==========

@app.route('/', methods=['GET'])
def root():
    """Información del API Gateway"""
    return jsonify({
        'service': 'API Gateway',
        'version': '1.0.0',
        'author': 'Alejandro De Mendoza',
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'users': '/api/users',
            'orders': '/api/orders',
            'payments': '/api/payments'
        },
        'architecture': 'Microservices',
        'communication': ['REST', 'RabbitMQ']
    }), 200

# ========== ERROR HANDLERS ==========

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)