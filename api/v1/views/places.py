#!/usr/bin/python3
"""Contains the places view for the API."""
from flask import jsonify, abort, request
from models import storage
from models.place import Place
from api.v1.views import app_views
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.user import User


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a Place object by place_id"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/cities/<city_id>/places', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    """Creates a new Place"""
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    if not request.is_json:
        abort(400, 'Not a JSON')
    data = request.get_json()
    if 'user_id' not in data:
        abort(400, 'Missing user_id')
    if 'name' not in data:
        abort(400, 'Missing name')
    user = storage.get(User, data['user_id'])
    if user is None:
        abort(404, 'User not found')
    place = Place(city_id=city_id, **data)
    storage.new(place)
    storage.save()
    return jsonify(place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    if not request.is_json:
        abort(400, 'Not a JSON')
    data = request.get_json()
    ignored_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignored_keys:
            setattr(place, key, value)
    place.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    """Deletes a Place object"""
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    storage.delete(place)
    storage.save()  # Ensure the changes are committed to the database
    return jsonify({}), 200


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def search_places():
    """Searches for Place objects based on JSON request body"""
    if not request.is_json:
        abort(400, description="Not a JSON")

    data = request.get_json()
    states = data.get('states', [])
    cities = data.get('cities', [])
    amenities = data.get('amenities', [])

    all_places = storage.all(Place).values()
    if not states and not cities and not amenities:
        return jsonify([place.to_dict() for place in all_places])

    place_ids = set()
    if states:
        for state_id in states:
            state = storage.get(State, state_id)
            if state:
                for city in state.cities:
                    place_ids.update(place.id for place in city.places)

    if cities:
        for city_id in cities:
            city = storage.get(City, city_id)
            if city:
                place_ids.update(place.id for place in city.places)

    if amenities:
        places_with_amenities = set()
        for amenity_id in amenities:
            amenity = storage.get(Amenity, amenity_id)
            if amenity:
                for place in all_places:
                    if amenity in place.amenities:
                        places_with_amenities.add(place.id)
        if not place_ids:
            place_ids = places_with_amenities
        else:
            place_ids.intersection_update(places_with_amenities)

    places = [storage.get(Place, place_id).to_dict() for place_id in place_ids]
    return jsonify(places)
