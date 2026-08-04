from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.notification import Notification

notification_bp = Blueprint('notification', __name__)

# Add OPTIONS handler
@notification_bp.route('/', methods=['OPTIONS'])
@notification_bp.route('/unread-count', methods=['OPTIONS'])
def handle_options():
    return jsonify({}), 200

@notification_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        user_id = get_jwt_identity()
        notifications = Notification.query.filter_by(
            user_id=user_id
        ).order_by(Notification.created_at.desc()).limit(50).all()
        
        return jsonify([n.to_dict() for n in notifications])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    try:
        user_id = get_jwt_identity()
        count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
        print(f"📊 Unread count: {count}")
        return jsonify({'unread_count': count})
    except Exception as e:
        print(f"❌ Error in unread-count: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/<int:id>/read', methods=['PUT'])
@jwt_required()
def mark_read(id):
    try:
        notification = Notification.query.get_or_404(id)
        notification.is_read = True
        db.session.commit()
        return jsonify({'message': 'Notification marked as read'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notification_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def mark_all_read():
    try:
        user_id = get_jwt_identity()
        Notification.query.filter_by(user_id=user_id, is_read=False).update(
            {'is_read': True}
        )
        db.session.commit()
        return jsonify({'message': 'All notifications marked as read'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500