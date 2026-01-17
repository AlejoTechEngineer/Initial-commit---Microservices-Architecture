from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from datetime import datetime

app = Flask(__name__)

# CORS (para desarrollo)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuración de URLs de microservicios (en Docker deben apuntar a nombres de servicio)
USER_SERVICE = os.getenv('USER_SERVICE_URL', 'http://user-service:5001')
ORDER_SERVICE = os.getenv('ORDER_SERVICE_URL', 'http://order-service:5002')
PAYMENT_SERVICE = os.getenv('PAYMENT_SERVICE_URL', 'http://payment-service:5003')


def safe_json(response):
    """Intenta parsear JSON, si no, devuelve texto crudo."""
    try:
        return response.json()
    except Exception:
        return {"raw": response.text}


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'timestamp': datetime.utcnow().isoformat()
    }), 200


@app.route('/status', methods=['GET'])
def status():
    services_status = {}

    for name, url in [
        ('user-service', USER_SERVICE),
        ('order-service', ORDER_SERVICE),
        ('payment-service', PAYMENT_SERVICE),
    ]:
        try:
            r = requests.get(f'{url}/health', timeout=2)
            services_status[name] = 'online' if r.status_code == 200 else 'degraded'
        except Exception:
            services_status[name] = 'offline'

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
    try:
        if request.method == 'GET':
            response = requests.get(f'{USER_SERVICE}/users')
        else:
            response = requests.post(f'{USER_SERVICE}/users', json=request.json)

        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'User service unavailable', 'message': str(e)}), 503


@app.route('/api/users/<user_id>', methods=['GET'])
def user_detail(user_id):
    try:
        response = requests.get(f'{USER_SERVICE}/users/{user_id}')
        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'User service unavailable', 'message': str(e)}), 503


# ========== ORDER SERVICE ROUTES ==========

@app.route('/api/orders', methods=['GET', 'POST'])
def orders():
    try:
        if request.method == 'GET':
            response = requests.get(f'{ORDER_SERVICE}/orders')
        else:
            response = requests.post(f'{ORDER_SERVICE}/orders', json=request.json)

        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Order service unavailable', 'message': str(e)}), 503


@app.route('/api/orders/<order_id>', methods=['GET'])
def order_detail(order_id):
    try:
        response = requests.get(f'{ORDER_SERVICE}/orders/{order_id}')
        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Order service unavailable', 'message': str(e)}), 503


@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def order_status(order_id):
    try:
        response = requests.put(f'{ORDER_SERVICE}/orders/{order_id}/status', json=request.json)
        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Order service unavailable', 'message': str(e)}), 503


# ========== PAYMENT SERVICE ROUTES ==========

@app.route('/api/payments', methods=['GET', 'POST'])
def payments():
    try:
        if request.method == 'GET':
            response = requests.get(f'{PAYMENT_SERVICE}/payments')
        else:
            response = requests.post(f'{PAYMENT_SERVICE}/payments', json=request.json)

        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Payment service unavailable', 'message': str(e)}), 503


@app.route('/api/payments/<payment_id>', methods=['GET'])
def payment_detail(payment_id):
    try:
        response = requests.get(f'{PAYMENT_SERVICE}/payments/{payment_id}')
        return jsonify(safe_json(response)), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({'error': 'Payment service unavailable', 'message': str(e)}), 503


@app.route('/', methods=['GET'])
def root():
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not Found', 'message': 'The requested endpoint does not exist'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal Server Error', 'message': 'An unexpected error occurred'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
