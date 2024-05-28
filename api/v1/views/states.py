#!/usr/bin/python3
"""Contains the states view for the API."""
from flask import jsonify, request, abort
from api.v1.views import app_views
from models import storage
from models.state import State


@app_views.route('/states', methods=['GET'], strict_slashes=False)
def get_states():
    """Retrieves the list of all State objects"""
    states = storage.all(State).values()
    return jsonify([state.to_dict() for state in states])


@app_views.route('/states/<state_id>', methods=['GET'], strict_slashes=False)
def get_state(state_id):
    """Retrieves a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404, description="State not found")
    return jsonify(state.to_dict())


@app_views.route('/states/<state_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_state(state_id):
    """Deletes a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404, description="State not found")
    try:
        storage.delete(state)
        storage.save()
    except Exception as e:
        abort(500, description="Internal server error: " + str(e))
    return jsonify({}), 200


@app_views.route('/states', methods=['POST'], strict_slashes=False)
def create_state():
    """Creates a State"""
    if not request.is_json:
        abort(400, description="Not a JSON")
    data = request.get_json()
    if 'name' not in data:
        abort(400, description="Missing name")
    try:
        new_state = State(**data)
        storage.new(new_state)
        storage.save()
    except Exception as e:
        abort(500, description="Internal server error: " + str(e))
    return jsonify(new_state.to_dict()), 201


@app_views.route('/states/<state_id>', methods=['PUT'], strict_slashes=False)
def update_state(state_id):
    """Updates a State object"""
    state = storage.get(State, state_id)
    if not state:
        abort(404, description="State not found")
    if not request.is_json:
        abort(400, description="Not a JSON")
    data = request.get_json()
    ignored_keys = ['id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignored_keys:
            setattr(state, key, value)
    try:
        state.save()
    except Exception as e:
        abort(500, description="Internal server error: " + str(e))
    return jsonify(state.to_dict()), 200
