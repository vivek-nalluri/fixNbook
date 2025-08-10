from flask import Flask, request, redirect, send_from_directory, jsonify, session, Response
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.json_util import dumps
from bson.binary import Binary
from flask_cors import CORS
import os
import stripe
import secrets

app = Flask(__name__)
# Generate a random 32-byte hex string for secret key
app.secret_key = secrets.token_hex(32)
CORS(app)

MONGO_URI = os.environ['MONGO_URI']
client = MongoClient(MONGO_URI)
db = client['service_booking']

stripe.api_key = os.environ['STRIPE_SECRET_KEY']

@app.route('/<path:filename>')
def serve_files(filename):
    return send_from_directory(os.getcwd(), filename)

@app.route('/')
def home():
    return open('index.html', 'r', encoding='utf-8').read()

@app.route('/provider-login', methods=['GET', 'POST'])
def provider_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        provider = db.providers.find_one({'email': email, 'password': password})
        if provider:
            session['provider_id'] = str(provider['_id'])
            session['provider_name'] = provider['name']
            return redirect('/provider-dashboard')
        else:
            return "Invalid Provider Credentials", 401

    return open('provider-login.html', 'r', encoding='utf-8').read()

@app.route('/provider-signup', methods=['GET', 'POST'])
def provider_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if db.providers.find_one({'email': email}):
            return "Email already registered for Provider!"
        
        db.providers.insert_one({'name': name, 'email': email, 'password': password})
        return redirect('/provider-login')

    return open('provider-signup.html', 'r', encoding='utf-8').read()

@app.route('/seeker-login', methods=['GET', 'POST'])
def seeker_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        seeker = db.seekers.find_one({'email': email, 'password': password})
        if seeker:
            session['seeker_id'] = str(seeker['_id'])
            session['seeker_name'] = seeker['name']
            return redirect('/seeker-dashboard')
        else:
            return "Invalid Seeker Credentials", 401

    return open('seeker-login.html', 'r', encoding='utf-8').read()

@app.route('/seeker-signup', methods=['GET', 'POST'])
def seeker_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        if db.seekers.find_one({'email': email}):
            return "Email already registered for Seeker!"
        
        db.seekers.insert_one({'name': name, 'email': email, 'password': password})
        return redirect('/seeker-login')

    return open('seeker-signup.html', 'r', encoding='utf-8').read()

@app.route('/provider-dashboard')
def provider_dashboard():
    if 'provider_id' not in session:
        return redirect('/provider-login')
    return send_from_directory(os.getcwd(), 'provider-dashboard.html')

# ---------- SERVICES LISTING & READ ----------

@app.route('/services', methods=['GET'])
def get_services():
    if 'provider_id' not in session and 'seeker_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'provider_id' in session:
        # Provider sees ONLY their services
        services = list(db.services.find({'provider_id': session['provider_id']}))
    else:
        # Seeker sees ALL services
        services = list(db.services.find())

    for s in services:
        s.pop('image', None)
        s['imageUrl'] = f"/services/image/{str(s['_id'])}" if 'image' in s else None

    return dumps(services), 200, {'Content-Type': 'application/json'}

@app.route('/services/<service_id>', methods=['GET'])
def get_service(service_id):
    try:
        oid = ObjectId(service_id)
    except:
        return jsonify({'error': 'Invalid ID'}), 400

    service = db.services.find_one({'_id': oid})
    if not service:
        return jsonify({'error': 'Service not found'}), 404

    # If provider, only allow read if it's theirs
    if 'provider_id' in session:
        if service.get('provider_id') != session['provider_id']:
            return jsonify({'error': 'Not found'}), 404

    # Seekers can read any
    service.pop('image', None)
    service['imageUrl'] = f"/services/image/{service_id}" if 'image' in service else None
    return dumps(service), 200, {'Content-Type': 'application/json'}

@app.route('/services/image/<service_id>')
def get_service_image(service_id):
    try:
        oid = ObjectId(service_id)
    except:
        return jsonify({'error': 'Invalid ID'}), 400

    service = db.services.find_one({'_id': oid})
    if not service or 'image' not in service:
        return jsonify({'error': 'Image not found'}), 404

    # If provider, only allow image if it's theirs
    if 'provider_id' in session:
        if service.get('provider_id') != session['provider_id']:
            return jsonify({'error': 'Not found'}), 404
    # Seekers can fetch any image

    image_data = service['image']
    return Response(image_data, mimetype='image/jpeg')

# ---------- CREATE / UPDATE / DELETE (OWNERSHIP ENFORCED) ----------

@app.route('/services', methods=['POST'])
def add_service():
    if 'provider_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    title = request.form.get('title')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    date = request.form.get('date')
    time = request.form.get('time')
    location = request.form.get('location')
    image_file = request.files.get('image')

    service_data = {
        'title': title,
        'description': description,
        'price': price,
        'date': date,
        'time': time,
        'location': location,
        'provider_id': session['provider_id']
    }

    if image_file:
        image_data = image_file.read()
        service_data['image'] = Binary(image_data)

    result = db.services.insert_one(service_data)
    return jsonify({'message': 'Service added', 'id': str(result.inserted_id)}), 201

@app.route('/services/<service_id>', methods=['PUT'])
def update_service(service_id):
    if 'provider_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        oid = ObjectId(service_id)
    except:
        return jsonify({'error': 'Invalid ID'}), 400

    # Ensure the service belongs to the logged-in provider
    owned = db.services.find_one({'_id': oid, 'provider_id': session['provider_id']})
    if not owned:
        return jsonify({'error': 'Not found or not yours'}), 404

    title = request.form.get('title')
    description = request.form.get('description')
    price = float(request.form.get('price'))
    date = request.form.get('date')
    time = request.form.get('time')
    location = request.form.get('location')
    image_file = request.files.get('image')

    update_data = {
        'title': title,
        'description': description,
        'price': price,
        'date': date,
        'time': time,
        'location': location,
    }

    if image_file:
        image_data = image_file.read()
        update_data['image'] = Binary(image_data)

    db.services.update_one({'_id': oid, 'provider_id': session['provider_id']}, {'$set': update_data})
    return jsonify({'message': 'Service updated'}), 200

@app.route('/services/<service_id>', methods=['DELETE'])
def delete_service(service_id):
    if 'provider_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        oid = ObjectId(service_id)
    except:
        return jsonify({'error': 'Invalid ID'}), 400

    result = db.services.delete_one({'_id': oid, 'provider_id': session['provider_id']})
    if result.deleted_count == 0:
        return jsonify({'error': 'Not found or not yours'}), 404

    return jsonify({'message': 'Service deleted'}), 200

# ---------- PAYMENTS & DASHBOARDS ----------

@app.route('/create-payment-intent', methods=['POST'])
def create_payment_intent():
    data = request.json
    amount = data.get('amount')
    if not amount:
        return jsonify({'error': 'Amount is required'}), 400
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='inr',
            payment_method_types=['card'],
        )
        return jsonify({'clientSecret': intent['client_secret']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/seeker-dashboard')
def seeker_dashboard():
    if 'seeker_id' not in session:
        return redirect('/seeker-login')
    return send_from_directory(os.getcwd(), 'seeker.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
