import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['GET'])
def get_drinks():
    drinks = Drink.query.all()

    if len(drinks)== 0:
        abort(404)

    formatted_drinks = [drink.short() for drink in drinks]

    return jsonify(
    {
        'success': True,
        'drinks': formatted_drinks
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
@requires_auth('get:drinks-detail')
def get_drinks_long(payload):
    drinks = Drink.query.all()

    if len(drinks)== 0:
        abort(404)

    formatted_drinks = [drink.long() for drink in drinks]

    return jsonify(
    {
        'success': True,
        'drinks': formatted_drinks
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
@requires_auth('post:drinks')
@app.route('/drinks', methods=['POST'])
def post_drinks():
    try:
        body = request.get_json()

        title = body.get('title', None)
        recipe = body.get('recipe', None)

        if not title or not recipe:
            abort(422)

        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()

        return jsonify(
        {
            'success': True,
            'drinks': [new_drink.long()]
        }), 200
    except Exception as e:
        print(e)
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
@requires_auth('patch:drinks')
@app.route('/drinks/<int:id>', methods=['PATCH'])
def patch_drinks(id):
    body = request.get_json()

    try:
        title = body.get('title', None)
        recipe = body.get('recipe', None)
        drink = Drink.query.filter(Drink.id==id).one_or_none()
        if drink is None:
            abort(404)

        drink.title = title
        drink.recipe = json.dumps(recipe)
        drink.update()

        formatted_drink = drink.long()
        return jsonify(
        {
            'success': True,
            'drinks': formatted_drink
        }), 200
    except Exception as e:
        print(e)
        abort(422)


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
@requires_auth('delete:drinks')
@app.route('/drinks/<int:id>', methods=['DELETE'])
def delete_drinks(id):
    drink = Drink.query.filter(Drink.id==id).one_or_none()

    if drink is None:
        abort(404)

    drink.delete()
    return jsonify(
    {
        'success': True,
        'delete': id
    }), 200

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404



'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success":False,
        "error":error.status_code,
        "message":error.error
    }),error.status_code


if __name__ == "__main__":
    app.debug = True
    app.run()
