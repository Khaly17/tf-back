from flask import Blueprint, request, jsonify
from app.item.models import Item, Notification, History, db
from app.auth.models import User
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.utils import add_history

item_bp = Blueprint('item', __name__)

@item_bp.route('/', methods=['POST'])
@jwt_required()
def create_item():
    data = request.get_json()
    user_id = get_jwt_identity()

    item = Item(
        type_id=data['type_id'],
        name=data['name'],
        unique_number=data['unique_number'],
        description=data.get('description'),
        status=data.get('status', 'lost'),
        owner_id=user_id
    )

    db.session.add(item)
    db.session.commit()
    add_history(item.id, "Item created")

    return jsonify({"message": "Item created", "id": item.id}), 201

@item_bp.route('/', methods=['GET'])
def get_all_items():
    items = Item.query.all()
    return jsonify([{
        "id": i.id,
        "type_id": i.type_id,
        "name": i.name,
        "unique_number": i.unique_number,
        "description": i.description,
        "status": i.status,
        "owner_id": i.owner_id
    } for i in items])

@item_bp.route('/<string:item_id>', methods=['GET'])
def get_item(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify({
        "id": item.id,
        "type_id": item.type_id,
        "name": item.name,
        "unique_number": item.unique_number,
        "description": item.description,
        "status": item.status,
        "owner_id": item.owner_id
    })

@item_bp.route('/<string:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    item = Item.query.get_or_404(item_id)
    user_id = get_jwt_identity()

    if item.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    item.type_id = data.get('type_id', item.type_id)
    item.name = data.get('name', item.name)
    item.unique_number = data.get('unique_number', item.unique_number)
    item.description = data.get('description', item.description)
    item.status = data.get('status', item.status)

    db.session.commit()
    add_history(item.id, "Item updated")
    return jsonify({"message": "Item updated"})

@item_bp.route('/<string:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    user_id = get_jwt_identity()

    if item.owner_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    add_history(item.id, "Item deleted")
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"})

@item_bp.route('/user/<string:user_id>', methods=['GET'])
def get_items_by_user(user_id):
    items = Item.query.filter_by(owner_id=user_id).all()
    return jsonify([{
        "id": i.id,
        "type_id": i.type_id,
        "name": i.name,
        "unique_number": i.unique_number,
        "description": i.description,
        "status": i.status
    } for i in items])

@item_bp.route('/search', methods=['GET'])
def search_item():
    unique_number = request.args.get('q')
    item = Item.query.filter_by(unique_number=unique_number).first()
    if item:
        return jsonify({
            "id": item.id,
            "type_id": item.type_id,
            "name": item.name,
            "unique_number": item.unique_number,
            "description": item.description,
            "status": item.status,
            "owner_id": item.owner_id
        })
    return jsonify({"message": "Item not found"}), 404


@item_bp.route('/notifications/', methods=['POST'])
@jwt_required()
def create_notification():
    data = request.get_json()
    user_id = get_jwt_identity()

    notification = Notification(
        user_id=user_id,
        item_id=data['item_id'],
        status=data.get('status', 'unread')
    )
    db.session.add(notification)
    db.session.commit()

    return jsonify({"message": "Notification created"}), 201

@item_bp.route('/notifications/', methods=['GET'])
def get_all_notifications():
    notifications = Notification.query.all()
    return jsonify([{
        "id": n.id,
        "user_id": n.user_id,
        "item_id": n.item_id,
        "status": n.status,
        "created_at": n.created_at
    } for n in notifications])

@item_bp.route('/notifications/user/<string:user_id>', methods=['GET'])
def get_notifications_by_user(user_id):
    notifications = Notification.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "id": n.id,
        "item_id": n.item_id,
        "status": n.status,
        "created_at": n.created_at
    } for n in notifications])

@item_bp.route('/notifications/<string:notification_id>', methods=['PUT'])
@jwt_required()
def update_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    data = request.get_json()
    notification.status = data.get('status', notification.status)
    db.session.commit()
    return jsonify({"message": "Notification updated"})

@item_bp.route('/notifications/<string:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({"message": "Notification deleted"})


@item_bp.route('/history/', methods=['POST'])
@jwt_required()
def create_history():
    data = request.get_json()
    user_id = get_jwt_identity()

    history = History(
        item_id=data['item_id'],
        user_id=user_id,
        action=data['action']
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({"message": "History created"}), 201

@item_bp.route('/history/', methods=['GET'])
def get_all_history():
    history = History.query.order_by(History.date.desc()).all()
    return jsonify([{
        "id": h.id,
        "item_id": h.item_id,
        "user_id": h.user_id,
        "action": h.action,
        "date": h.date
    } for h in history])

@item_bp.route('/history/item/<string:item_id>', methods=['GET'])
def get_history_by_item(item_id):
    history = History.query.filter_by(item_id=item_id).order_by(History.date.desc()).all()
    return jsonify([{
        "id": h.id,
        "user_id": h.user_id,
        "action": h.action,
        "date": h.date
    } for h in history])

@item_bp.route('/history/user/<string:user_id>', methods=['GET'])
def get_history_by_user(user_id):
    history = History.query.filter_by(user_id=user_id).order_by(History.date.desc()).all()
    return jsonify([{
        "id": h.id,
        "item_id": h.item_id,
        "action": h.action,
        "date": h.date
    } for h in history])


@item_bp.route('/owner-by-number', methods=['GET'])
def get_user_by_item_number():
    unique_number = request.args.get('q')
    if not unique_number:
        return jsonify({"error": "Missing unique number"}), 400

    item = Item.query.filter_by(unique_number=unique_number).first()
    if not item:
        return jsonify({"error": "Item not found"}), 404

    user = User.query.get(item.owner_id)
    if not user:
        return jsonify({"error": "Owner not found"}), 404

    return jsonify({
        "owner": {
            "id": user.id,
            "last_name": user.last_name,
            "first_name": user.first_name,
            "email": user.email,
            "phone": user.phone
        },
        "item": {
            "id": item.id,
            "name": item.name,
            "unique_number": item.unique_number,
            "description": item.description,
            "status": item.status
        }
    })
