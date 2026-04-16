import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from sqlalchemy.dialects.postgresql import insert
from flask_jwt_extended import jwt_required, get_jwt_identity

from application import db
from app.models.regulatory_update import RegulatoryUpdate, UserUpdateReadStatus, UpdateSubscription
from app.models.user import User
from app.services.ai_service import generate_simple_summary
from app.services.ai_service import generate_simple_summary, extract_obligations

updates_bp = Blueprint('updates', __name__)

# Enterprise API Key Auth for n8n
N8N_WEBHOOK_SECRET = os.getenv('N8N_WEBHOOK_SECRET', 'super-secret-n8n-key-change-in-production')


@updates_bp.route('/webhook/n8n/updates', methods=['POST'])
def ingest_updates():
    """Endpoint for n8n to push daily regulatory updates."""
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {N8N_WEBHOOK_SECRET}":
        return jsonify({'error': 'Unauthorized. Invalid API Key.'}), 401

    payload = request.get_json()
    if not payload or not isinstance(payload, list):
        return jsonify({'error': 'Invalid payload format. Expected an array.'}), 400

    insert_values = []
    for batch in payload:
        generated_at_str = batch.get('generated_at')
        try:
            generated_at = datetime.fromisoformat(generated_at_str.replace('Z', '+00:00')) if generated_at_str else datetime.utcnow()
        except (ValueError, TypeError):
            generated_at = datetime.utcnow()

        articles = batch.get('data', [])
        for item in articles:
            url = item.get('url')
            if not url:
                continue
                
            insert_values.append({
                'country': item.get('country'),
                'regulator': item.get('regulator'),
                'title': item.get('title'),
                'summary': item.get('summary'),
                'impact': item.get('impact'),
                'url': url,
                'generated_at': generated_at,
                'created_at': datetime.utcnow()
            })

    if not insert_values:
        return jsonify({'status': 'success', 'message': 'No valid updates found in payload.'}), 200

    try:
        # UPSERT (Deduplication)
        stmt = insert(RegulatoryUpdate).values(insert_values)
        stmt = stmt.on_conflict_do_nothing(index_elements=['url'])
        db.session.execute(stmt)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Successfully processed batch of {len(insert_values)} updates.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@updates_bp.route('/', methods=['GET'])
@jwt_required()
def get_updates():
    """Get paginated regulatory updates with user-specific read status."""
    user_id = get_jwt_identity()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    country = request.args.get('country')
    impact = request.args.get('impact')
    regulator = request.args.get('regulator')
    search = request.args.get('search')
    
    query = RegulatoryUpdate.query
    if country: query = query.filter(RegulatoryUpdate.country.ilike(f"%{country}%"))
    if impact: query = query.filter(RegulatoryUpdate.impact.ilike(f"{impact}"))
    if regulator: query = query.filter(RegulatoryUpdate.regulator.ilike(f"%{regulator}%"))
    if search:
        query = query.filter((RegulatoryUpdate.title.ilike(f"%{search}%")) | (RegulatoryUpdate.summary.ilike(f"%{search}%")))
        
    query = query.order_by(RegulatoryUpdate.generated_at.desc())
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Optimized Status Fetching
    update_ids = [u.id for u in paginated.items]
    statuses = UserUpdateReadStatus.query.filter(
        UserUpdateReadStatus.user_id == user_id, 
        UserUpdateReadStatus.update_id.in_(update_ids)
    ).all()
    status_map = {s.update_id: s for s in statuses}
    
    results = []
    for update in paginated.items:
        data = update.to_dict()
        user_status = status_map.get(update.id)
        data['user_status'] = {
            'is_read': user_status.is_read if user_status else False,
            'is_acknowledged': user_status.is_acknowledged if user_status else False,
            'read_at': user_status.read_at.isoformat() if user_status and user_status.read_at else None
        }
        results.append(data)
        
    return jsonify({
        'status': 'success',
        'data': results,
        'meta': {'page': page, 'per_page': per_page, 'total_pages': paginated.pages, 'total_items': paginated.total}
    }), 200

@updates_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get the total count of unread updates for the UI Notification Badge."""
    user_id = get_jwt_identity()
    total_updates = RegulatoryUpdate.query.count()
    read_count = UserUpdateReadStatus.query.filter_by(user_id=user_id, is_read=True).count()
    return jsonify({'status': 'success', 'unread_count': max(0, total_updates - read_count)}), 200

@updates_bp.route('/<int:update_id>/status', methods=['POST'])
@jwt_required()
def update_read_status(update_id):
    """Mark an update as Read or Acknowledged."""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'action' not in data:
        return jsonify({'error': 'Missing action (read or acknowledge)'}), 400
        
    action = data['action'].lower()
    if action not in ['read', 'acknowledge']:
        return jsonify({'error': 'Invalid action'}), 400

    update_record = RegulatoryUpdate.query.get(update_id)
    if not update_record: return jsonify({'error': 'Update not found'}), 404

    status_record = UserUpdateReadStatus.query.filter_by(user_id=user_id, update_id=update_id).first()
    if not status_record:
        status_record = UserUpdateReadStatus(user_id=user_id, update_id=update_id)
        db.session.add(status_record)

    now = datetime.utcnow()
    if action == 'read' and not status_record.is_read:
        status_record.is_read = True
        status_record.read_at = now
    elif action == 'acknowledge' and not status_record.is_acknowledged:
        status_record.is_acknowledged = True
        status_record.acknowledged_at = now
        if not status_record.is_read:
            status_record.is_read = True
            status_record.read_at = now

    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Update marked as {action}', 'data': status_record.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500


@updates_bp.route('/subscribe', methods=['POST'])
@jwt_required(optional=True)
def subscribe():
    """
    Subscribe a user to regulatory updates.
    POST /api/updates/subscribe
    """
    data = request.get_json() or {}
    email = data.get('email')
    current_user_id = get_jwt_identity()
    
    # Auto-resolve email if logged in but no email provided
    if not email and current_user_id:
        user = User.query.get(current_user_id)
        if user:
            email = user.email

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    # Upsert Subscription
    sub = UpdateSubscription.query.filter_by(email=email).first()
    if sub:
        sub.preferences = data.get('preferences', sub.preferences)
        sub.is_active = True
        if current_user_id and not sub.user_id:
            sub.user_id = current_user_id
    else:
        sub = UpdateSubscription(
            email=email,
            user_id=current_user_id,
            preferences=data.get('preferences', {})
        )
        db.session.add(sub)
        
    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Subscribed successfully', 'data': sub.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@updates_bp.route('/webhook/n8n/subscribers', methods=['GET'])
def get_n8n_subscribers():
    """
    Webhook for n8n to pull the active subscriber mailing list.
    GET /api/updates/webhook/n8n/subscribers
    """
    auth_header = request.headers.get('Authorization')
    if auth_header != f"Bearer {N8N_WEBHOOK_SECRET}":
        return jsonify({'error': 'Unauthorized. Invalid API Key.'}), 401

    subs = UpdateSubscription.query.filter_by(is_active=True).all()
    
    return jsonify({
        'status': 'success',
        'count': len(subs),
        'subscribers': [s.to_dict() for s in subs]
    }), 200
    
@updates_bp.route('/<int:update_id>/summarize', methods=['POST'])
@jwt_required()
def generate_single_summary(update_id):
    """
    Generates an AI summary for a specific regulatory update on-demand.
    POST /api/updates/<update_id>/summarize
    """
    # 1. Fetch the specific update
    update_record = RegulatoryUpdate.query.get(update_id)
    if not update_record:
        return jsonify({'error': 'Update not found'}), 404

    # 2. Check if it already has a summary (saves API costs if clicked twice)
    if update_record.ai_one_liner:
        return jsonify({
            'status': 'success',
            'message': 'Summary already exists',
            'data': {
                'id': update_record.id,
                'ai_one_liner': update_record.ai_one_liner
            }
        }), 200

    # 3. Process through the LLM
    combined_text = f"Title: {update_record.title}\nDetails: {update_record.summary}"
    simple_summary = generate_simple_summary(combined_text)

    if not simple_summary:
        return jsonify({'error': 'Failed to generate AI summary from OpenAI'}), 500

    # 4. Save and return
    update_record.ai_one_liner = simple_summary
    
    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'AI Summary generated successfully',
            'data': {
                'id': update_record.id,
                'ai_one_liner': update_record.ai_one_liner
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database save failed: {str(e)}'}), 500

@updates_bp.route('/<int:update_id>/extract-obligations', methods=['POST'])
@jwt_required()
def generate_obligations(update_id):
    """
    Extracts actionable obligations from a specific regulatory update on-demand.
    POST /api/updates/<update_id>/extract-obligations
    """
    update_record = RegulatoryUpdate.query.get(update_id)
    if not update_record:
        return jsonify({'error': 'Update not found'}), 404

    # 1. Check if obligations already exist (Save API costs!)
    # We check if it's not None AND if it has items in the list
    if update_record.obligations is not None and len(update_record.obligations) > 0:
        return jsonify({
            'status': 'success',
            'message': 'Obligations already extracted',
            'data': {
                'id': update_record.id,
                'obligations': update_record.obligations
            }
        }), 200

    # 2. Process through LLM
    combined_text = f"Title: {update_record.title}\nDetails: {update_record.summary}"
    extracted_obligations = extract_obligations(combined_text)

    if extracted_obligations is None:
        return jsonify({'error': 'Failed to extract obligations from OpenAI'}), 500

    # 3. Save to the JSON column and return minimal payload
    update_record.obligations = extracted_obligations
    
    try:
        db.session.commit()
        return jsonify({
            'status': 'success',
            'message': 'Obligations extracted successfully',
            'data': {
                'id': update_record.id,
                'obligations': update_record.obligations
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database save failed: {str(e)}'}), 500