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


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
def get_drinks_detail():
	entity_list = Drink.query.all()
	drinks = [entity.long() for entity in entity_list]

	return jsonify({
		'success': True,
		'drinks': drinks
	})

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
def create_drink():
	try:
		props = request.get_json()
		drink = Drink(props)
		drink.insert()

		return jsonify({
			'success': True,
			'drinks': [drink.long()]
		}), 201

	except:
		abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
def update_drink(id):
	props = request.get_json()
	drink = Drink.query.get_or_404(id)
	drink.title = props['title']
	drink.recipe = props['recipe']
	drink.update()

	return jsonify({
		'success': True,
		'drinks': [drink.long()]
	})

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drink(id):
	drink = Drink.query.get_or_404(id)
	drink.delete()

	return jsonify({
		'success': True,
		'delete': id
	})

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
	return jsonify({
		"success": False,
		"error": 422,
		"message": "unprocessable"
	}), 422


@app.errorhandler(HTTPException)
def handle_exception(e):
	"""Return JSON instead of HTML for HTTP errors."""
	# start with the correct headers and status code from the error
	response = e.get_response()
	# replace the body with JSON
	response.data = json.dumps({
		"success": False,
		"error": e.code,
		"message": e.description,
	})
	response.content_type = "application/json"
	return response

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
