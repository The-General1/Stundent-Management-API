from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt_claims

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'secret-p@ss' 
jwt = JWTManager(app)

@app.route('/protected')
@jwt_required
def protected():
    user_id = get_jwt_identity()
    user_roles = get_jwt_claims().get('roles', [])

    if 'admin' not in user_roles:
        return jsonify({'message': 'You are not authorized to access this endpoint'}), 403

    return jsonify({'message': 'You are authorized to access this endpoint!'}), 200


users = [
    {'id': 1, 'username': 'alice', 'password': 'password1', 'roles': ['admin']},
    {'id': 2, 'username': 'bob', 'password': 'password2', 'roles': ['user']}
]

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    user = next((user for user in users if user['username'] == username and user['password'] == password), None)

    if user is None:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity=user['id'], user_claims={'roles': user['roles']})
    return jsonify({'access_token': access_token}), 200
