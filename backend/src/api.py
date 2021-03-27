import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

# db_drop_and_create_all()

# ROUTES
@app.route('/drinks', methods=['GET'])
def get_drinks():
	entity_list = Drink.query.all()
	drinks = [entity.short() for entity in entity_list]

	return jsonify({
		'success': True,
		'drinks': drinks
	})

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
	entity_list = Drink.query.all()
	drinks = [entity.long() for entity in entity_list]

	return jsonify({
		'success': True,
		'drinks': drinks
	})

@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
	props = request.get_json()
	props['recipe'] = json.dumps(props['recipe'], separators=(',', ':'))
	drink = Drink(props)
	drink.insert()

	return jsonify({
		'success': True,
		'drinks': [drink.long()]
	})

@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, id):
	props = request.get_json()
	drink = Drink.query.get_or_404(id)
	drink.title = props.get('title', drink.title)
	drink.recipe = props.get('recipe', '[]')
	drink.update()

	return jsonify({
		'success': True,
		'drinks': [drink.long()]
	})

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, id):
	drink = Drink.query.get_or_404(id)
	drink.delete()

	return jsonify({
		'success': True,
		'delete': id
	})

@app.errorhandler(Exception)
def handle_error(e):
	status_code = 500
	message = str(e)
	code = None

	if isinstance(e, HTTPException):
		status_code = e.code
	
	if isinstance(e, AuthError):
		status_code = e.status_code
		code = e.error['code']
		message = e.error['description']

	return jsonify({
		'success': False,
		'error': status_code,
		'code': code,
		'message': message,
	}), status_code
