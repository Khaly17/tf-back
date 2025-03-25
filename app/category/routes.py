from flask import Blueprint, request, jsonify
from app.category.models import Category, db
from flask_jwt_extended import jwt_required

category_bp = Blueprint('category', __name__)

@category_bp.route('/', methods=['POST'])
@jwt_required()
def create_category():
    data = request.get_json()
    name = data.get('name')

    if not name:
        return jsonify({"error": "Name is required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 409

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return jsonify({"message": "Category created", "id": category.id}), 201

@category_bp.route('/', methods=['GET'])
def get_all_categories():
    categories = Category.query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name
    } for c in categories])

@category_bp.route('/<string:category_id>', methods=['GET'])
def get_category(category_id):
    category = Category.query.get_or_404(category_id)
    return jsonify({
        "id": category.id,
        "name": category.name
    })

@category_bp.route('/<string:category_id>', methods=['PUT'])
@jwt_required()
def update_category(category_id):
    category = Category.query.get_or_404(category_id)
    data = request.get_json()
    new_name = data.get('name')

    if new_name:
        category.name = new_name
        db.session.commit()
        return jsonify({"message": "Category updated"})
    else:
        return jsonify({"error": "Name is required"}), 400

@category_bp.route('/<string:category_id>', methods=['DELETE'])
@jwt_required()
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category deleted"})
