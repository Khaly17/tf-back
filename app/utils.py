from app.item.models import History, db
from flask_jwt_extended import get_jwt_identity
from datetime import datetime

def add_history(item_id, action, user_id=None):
    if not user_id:
        user_id = get_jwt_identity()

    history = History(
        item_id=item_id,
        user_id=user_id,
        action=action,
        date=datetime.utcnow()
    )
    db.session.add(history)
    db.session.commit()
