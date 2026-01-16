from flask import Flask, jsonify, request
from datetime import datetime
import os
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Configuración de MongoDB
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/orderdb')

def get_db():
    """Conexión a MongoDB"""
    try:
        client = MongoClient(MONGODB_URL)
        db = client.get_database()
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def init_db():
    """Inicializar colección de pedidos"""
    db = get_db()
    if db:
        try:
            # Crear colección si no existe
            if 'orders' not in db.list_collection_names():
                db.create_collection('orders')
            
            # Crear índice en user_id
            db.orders.create_index('user_id')
            print("✅ Order collection initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing MongoDB: {e}")

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    db_status = 'connected'
    db = get_db()
    if not db:
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'healthy',
        'service': 'order-service',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint detallado"""
    db = get_db()
    order_count = 0
    
    if db:
        try:
            order_count = db.orders.count_documents({})
        except:
            order_count = 0
    
    return jsonify({
        'service': 'order-service',
        'status': 'operational',
        'database': 'MongoDB',
        'total_orders': order_count,
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    """Obtener todos los pedidos"""
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        orders = list(db.orders.find())
        
        # Convertir ObjectId a string para JSON
        for order in orders:
            order['_id'] = str(order['_id'])
        
        return jsonify({
            'success': True,
            'count': len(orders),
            'orders': orders
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['POST'])
def create_order():
    """Crear nuevo pedido"""
    data = request.get_json()
    
    if not data or 'user_id' not in data or 'items' not in data:
        return jsonify({
            'error': 'Missing required fields: user_id, items'
        }), 400
    
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        # Crear documento de pedido
        order = {
            'user_id': data['user_id'],
            'items': data['items'],
            'total': data.get('total', 0),
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = db.orders.insert_one(order)
        order['_id'] = str(result.inserted_id)
        
        # TODO: Publicar evento OrderCreated en RabbitMQ
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Obtener pedido por ID"""
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        order = db.orders.find_one({'_id': ObjectId(order_id)})
        
        if order:
            order['_id'] = str(order['_id'])
            return jsonify({
                'success': True,
                'order': order
            }), 200
        else:
            return jsonify({
                'error': 'Order not found'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Actualizar estado del pedido"""
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({
            'error': 'Missing required field: status'
        }), 400
    
    db = get_db()
    if not db:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        result = db.orders.update_one(
            {'_id': ObjectId(order_id)},
            {
                '$set': {
                    'status': data['status'],
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': 'Order status updated successfully'
            }), 200
        else:
            return jsonify({
                'error': 'Order not found or status unchanged'
            }), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def root():
    """Información del servicio"""
    return jsonify({
        'service': 'Order Service',
        'version': '1.0.0',
        'database': 'MongoDB',
        'author': 'Alejandro De Mendoza',
        'endpoints': {
            'health': '/health',
            'status': '/status',
            'orders': '/orders [GET, POST]',
            'order_detail': '/orders/<id> [GET]',
            'update_status': '/orders/<id>/status [PUT]'
        }
    }), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5002, debug=True)