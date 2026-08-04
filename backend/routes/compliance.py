from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.db import db
from models.compliance import Compliance
from datetime import datetime, date, timedelta  # ✅ Added timedelta
from sqlalchemy import func, or_

compliance_bp = Blueprint('compliance', __name__)

# Add OPTIONS handler for all routes
@compliance_bp.route('/', methods=['OPTIONS'])
@compliance_bp.route('/stats', methods=['OPTIONS'])
@compliance_bp.route('/<int:id>', methods=['OPTIONS'])
def handle_options():
    return jsonify({}), 200

@compliance_bp.route('/', methods=['GET'])
@jwt_required()
def get_compliance():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Compliance.query
        
        if search:
            query = query.filter(
                or_(
                    Compliance.compliance_name.ilike(f'%{search}%'),
                    Compliance.authority.ilike(f'%{search}%')
                )
            )
        
        total = query.count()
        items = query.order_by(Compliance.valid_date.asc()).offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'data': [c.to_dict() for c in items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page if total > 0 else 1
            }
        })
    except Exception as e:
        print(f"❌ Error in get_compliance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@compliance_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    try:
        print("📊 Fetching stats...")
        
        total = Compliance.query.count()
        completed = Compliance.query.filter_by(status='Completed').count()
        ongoing = Compliance.query.filter_by(status='Ongoing').count()
        planned = Compliance.query.filter_by(status='Planned').count()
        overdue = Compliance.query.filter_by(status='Overdue').count()
        
        today = date.today()
        month_start = date(today.year, today.month, 1)
        due_this_month = Compliance.query.filter(
            Compliance.valid_date >= month_start,
            Compliance.valid_date <= today,
            Compliance.status != 'Completed'
        ).count()
        
        category_stats = db.session.query(
            Compliance.category,
            func.count(Compliance.id).label('count')
        ).group_by(Compliance.category).all()
        
        result = {
            'total': total,
            'completed': completed,
            'ongoing': ongoing,
            'planned': planned,
            'overdue': overdue,
            'due_this_month': due_this_month,
            'completion_rate': round((completed / total * 100) if total > 0 else 0, 2),
            'category_stats': [{'category': c[0], 'count': c[1]} for c in category_stats],
            'monthly_stats': []
        }
        
        print(f"✅ Stats: total={total}, completed={completed}, ongoing={ongoing}, overdue={overdue}")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in get_stats: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ✅ UPDATED: Create Compliance with Reminder Fields
@compliance_bp.route('/', methods=['POST'])
@jwt_required()
def create_compliance():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        required = ['authority', 'compliance_name', 'category', 'valid_date']
        for field in required:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        valid_date = datetime.strptime(data['valid_date'], '%Y-%m-%d').date()
        
        # Parse reminder_1_date if provided
        reminder_1_date = None
        if data.get('reminder_1_date'):
            reminder_1_date = datetime.strptime(data['reminder_1_date'], '%Y-%m-%d').date()
        
        # Auto-calculate reminder 2 and 3 dates
        reminder_2_date = valid_date - timedelta(days=5)
        reminder_3_date = valid_date - timedelta(days=2)
        
        compliance = Compliance(
            authority=data['authority'],
            compliance_name=data['compliance_name'],
            category=data['category'],
            valid_date=valid_date,
            submission_date=datetime.strptime(data['submission_date'], '%Y-%m-%d').date() if data.get('submission_date') else None,
            process_time=data.get('process_time'),
            frequency=data.get('frequency', 'OneTime'),
            reminder_days=data.get('reminder_days', '30,15,7,3,1'),
            priority=data.get('priority', 'Medium'),
            status=data.get('status', 'Planned'),
            remarks=data.get('remarks'),
            updated_by=str(user_id),
            # ✅ NEW FIELDS
            reminder_1_date=reminder_1_date,
            reminder_2_date=reminder_2_date,
            reminder_3_date=reminder_3_date,
            reminder_1_sent=False,
            reminder_2_sent=False,
            reminder_3_sent=False
        )
        
        db.session.add(compliance)
        db.session.commit()
        
        return jsonify(compliance.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ✅ UPDATED: Update Compliance with Reminder Fields
@compliance_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_compliance(id):
    try:
        compliance = Compliance.query.get_or_404(id)
        data = request.get_json()
        user_id = get_jwt_identity()
        
        # Existing fields
        if 'authority' in data:
            compliance.authority = data['authority']
        if 'compliance_name' in data:
            compliance.compliance_name = data['compliance_name']
        if 'category' in data:
            compliance.category = data['category']
        if 'valid_date' in data:
            compliance.valid_date = datetime.strptime(data['valid_date'], '%Y-%m-%d').date()
            # Recalculate reminder 2 and 3 when valid date changes
            compliance.reminder_2_date = compliance.valid_date - timedelta(days=5)
            compliance.reminder_3_date = compliance.valid_date - timedelta(days=2)
            # Reset sent flags when date changes
            compliance.reminder_2_sent = False
            compliance.reminder_3_sent = False
        if 'submission_date' in data and data['submission_date']:
            compliance.submission_date = datetime.strptime(data['submission_date'], '%Y-%m-%d').date()
        if 'process_time' in data:
            compliance.process_time = data['process_time']
        if 'frequency' in data:
            compliance.frequency = data['frequency']
        if 'reminder_days' in data:
            compliance.reminder_days = data['reminder_days']
        if 'priority' in data:
            compliance.priority = data['priority']
        if 'status' in data:
            compliance.status = data['status']
            if data['status'] == 'Completed':
                compliance.completion_date = date.today()
        if 'remarks' in data:
            compliance.remarks = data['remarks']
        
        # ✅ NEW: Update reminder_1_date if provided
        if 'reminder_1_date' in data:
            if data['reminder_1_date']:
                compliance.reminder_1_date = datetime.strptime(data['reminder_1_date'], '%Y-%m-%d').date()
                # Reset sent flag when date changes
                compliance.reminder_1_sent = False
            else:
                compliance.reminder_1_date = None
        
        compliance.updated_by = str(user_id)
        db.session.commit()
        
        return jsonify(compliance.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@compliance_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_compliance(id):
    try:
        compliance = Compliance.query.get_or_404(id)
        db.session.delete(compliance)
        db.session.commit()
        return jsonify({'message': 'Compliance deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500