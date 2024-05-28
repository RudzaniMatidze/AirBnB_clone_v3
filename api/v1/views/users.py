#!/usr/bin/python3
"""Contains the users view for the API."""
from flask import jsonify, abort, request
from models import storage
from models.user import User
from api.v1.views import app_views


@app_views.route('/users', methods=['GET'], strict_slashes=False)
def get_users():
    """Retrieves the list of all User objects"""
    users = storage.all(User).values()
    return jsonify([user.to_dict() for user in users])


@app_views.route('/users/<user_id>', methods=['GET'], strict_slashes=False)
def get_user(user_id):
    """Retrieves a User object by user_id"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    return jsonify(user.to_dict())


@app_views.route('/users', methods=['POST'], strict_slashes=False)
def create_user():
    """Creates a new User"""
    if not request.is_json:
        abort(400, description='Not a JSON')
    data = request.get_json()
    if 'email' not in data:
        abort(400, description='Missing email')
    if 'password' not in data:
        abort(400, description='Missing password')
    try:
        user = User(**data)
        storage.new(user)
        storage.save()
    except Exception as e:
        abort(500, description="Internal server error: " + str(e))
    return jsonify(user.to_dict()), 201


@app_views.route('/users/<user_id>', methods=['PUT'], strict_slashes=False)
def update_user(user_id):
    """Updates a User object"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    if not request.is_json:
        abort(400, description='Not a JSON')
    data = request.get_json()
    ignored_keys = ['id', 'email', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignored_keys:
            setattr(user, key, value)
    try:
        user.save()
    except Exception as e:
        abort(500, description="Internal server error: " + str(e))
    return jsonify(user.to_dict()), 200


@app_views.route('/users/<user_id>', methods=['DELETE'], strict_slashes=False)
def delete_user(user_id):
    """Deletes a User object"""
    user = storage.get(User, user_id)
    if user is None:
        abort(404, description="User not found")
    try:
        storage.delete(user)
        storage.save()
    except Exception as e:
        abort(500, description="Internal server error: " + str(e))
    return jsonify({}), 200
