#!/usr/bin/python3
"""Contains the places_reviews view for the API."""
from flask import Flask, jsonify, abort, request
from api.v1.views import app_views
from models import storage, Place, Review


@app_views.route('/places/<place_id>/reviews', methods=['GET'])
def get_reviews_by_place(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    reviews = [review.to_dict() for review in place.reviews]
    return jsonify(reviews)


@app_views.route('/reviews/<review_id>', methods=['GET'])
def get_review(review_id):
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    storage.delete(review)
    storage.save()
    return jsonify({}), 200


@app_views.route('/places/<place_id>/reviews', methods=['POST'])
def create_review(place_id):
    place = storage.get(Place, place_id)
    if not place:
        abort(404)

    if not request.is_json:
        abort(400, "Not a JSON")

    data = request.get_json()
    if 'user_id' not in data:
        abort(400, "Missing user_id")
    if 'text' not in data:
        abort(400, "Missing text")

    user_id = data['user_id']
    user = storage.get(User, user_id)
    if not user:
        abort(404)

    review = Review(**data)
    review.place_id = place_id
    storage.new(review)
    storage.save()
    return jsonify(review.to_dict()), 201


@app_views.route('/reviews/<review_id>', methods=['PUT'])
def update_review(review_id):
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    if not request.is_json:
        abort(400, "Not a JSON")

    data = request.get_json()
    ignored_keys = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignored_keys:
            setattr(review, key, value)

    storage.save()
    return jsonify(review.to_dict()), 200
