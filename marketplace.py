from flask import Blueprint, request, jsonify
from src.models.marketplace import Marketplace, db
from src.models.user import User
from datetime import datetime
import uuid

marketplace_bp = Blueprint('marketplace', __name__)

@marketplace_bp.route('/marketplaces', methods=['GET'])
def get_marketplaces():
    """Get all marketplaces with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '')
        type_filter = request.args.get('type', 'all')
        priority_filter = request.args.get('priority', 'all')
        status_filter = request.args.get('status', 'all')
        favorites_only = request.args.get('favorites', 'false').lower() == 'true'
        
        # Build query
        query = Marketplace.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Marketplace.name.ilike(f'%{search}%'),
                    Marketplace.description.ilike(f'%{search}%')
                )
            )
        
        if type_filter != 'all':
            query = query.filter(Marketplace.type == type_filter)
        
        if priority_filter != 'all':
            query = query.filter(Marketplace.priority == priority_filter)
        
        if status_filter == 'active':
            query = query.filter(Marketplace.active == True)
        elif status_filter == 'inactive':
            query = query.filter(Marketplace.active == False)
        
        if favorites_only:
            query = query.filter(Marketplace.favorite == True)
        
        # Execute query
        marketplaces = query.order_by(Marketplace.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [marketplace.to_dict() for marketplace in marketplaces],
            'total': len(marketplaces)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@marketplace_bp.route('/marketplaces', methods=['POST'])
def create_marketplace():
    """Create a new marketplace"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Nome é obrigatório'
            }), 400
        
        if not data.get('type'):
            return jsonify({
                'success': False,
                'error': 'Tipo é obrigatório'
            }), 400
        
        # Generate ID if not provided
        if not data.get('id'):
            data['id'] = str(uuid.uuid4())
        
        # Check if ID already exists
        existing = Marketplace.query.get(data['id'])
        if existing:
            return jsonify({
                'success': False,
                'error': 'ID já existe'
            }), 400
        
        # Create marketplace
        marketplace = Marketplace.create_from_dict(data)
        db.session.add(marketplace)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': marketplace.to_dict(),
            'message': 'Marketplace criado com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@marketplace_bp.route('/marketplaces/<marketplace_id>', methods=['GET'])
def get_marketplace(marketplace_id):
    """Get a specific marketplace"""
    try:
        marketplace = Marketplace.query.get(marketplace_id)
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': marketplace.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@marketplace_bp.route('/marketplaces/<marketplace_id>', methods=['PUT'])
def update_marketplace(marketplace_id):
    """Update a marketplace"""
    try:
        marketplace = Marketplace.query.get(marketplace_id)
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            marketplace.name = data['name']
        if 'description' in data:
            marketplace.description = data['description']
        if 'color' in data:
            marketplace.color = data['color']
        if 'logoUrl' in data:
            marketplace.logo_url = data['logoUrl']
        if 'type' in data:
            marketplace.type = data['type']
        if 'priority' in data:
            marketplace.priority = data['priority']
        if 'tags' in data:
            marketplace.tags = json.dumps(data['tags'])
        if 'responsible' in data:
            marketplace.responsible = data['responsible']
        if 'active' in data:
            marketplace.active = data['active']
        if 'favorite' in data:
            marketplace.favorite = data['favorite']
        
        # Update URLs
        if 'urls' in data:
            urls = data['urls']
            marketplace.admin_url = urls.get('admin')
            marketplace.reports_url = urls.get('reports')
            marketplace.other_url = urls.get('other')
        
        # Update schedule
        if 'schedule' in data:
            schedule = data['schedule']
            marketplace.schedule_start = schedule.get('start')
            marketplace.schedule_end = schedule.get('end')
        
        if 'timezone' in data:
            marketplace.timezone = data['timezone']
        
        if 'customFields' in data:
            marketplace.custom_fields = json.dumps(data['customFields'])
        
        marketplace.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': marketplace.to_dict(),
            'message': 'Marketplace atualizado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@marketplace_bp.route('/marketplaces/<marketplace_id>', methods=['DELETE'])
def delete_marketplace(marketplace_id):
    """Delete a marketplace"""
    try:
        marketplace = Marketplace.query.get(marketplace_id)
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 404
        
        # Check if marketplace has associated routines or tasks
        if marketplace.routines or marketplace.tasks:
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir marketplace com rotinas ou tarefas associadas'
            }), 400
        
        db.session.delete(marketplace)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Marketplace excluído com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@marketplace_bp.route('/marketplaces/<marketplace_id>/toggle-favorite', methods=['POST'])
def toggle_favorite(marketplace_id):
    """Toggle marketplace favorite status"""
    try:
        marketplace = Marketplace.query.get(marketplace_id)
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 404
        
        marketplace.favorite = not marketplace.favorite
        marketplace.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': marketplace.to_dict(),
            'message': f'Marketplace {"adicionado aos" if marketplace.favorite else "removido dos"} favoritos'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@marketplace_bp.route('/marketplaces/<marketplace_id>/toggle-active', methods=['POST'])
def toggle_active(marketplace_id):
    """Toggle marketplace active status"""
    try:
        marketplace = Marketplace.query.get(marketplace_id)
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 404
        
        marketplace.active = not marketplace.active
        marketplace.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': marketplace.to_dict(),
            'message': f'Marketplace {"ativado" if marketplace.active else "desativado"}'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

