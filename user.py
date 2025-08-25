from flask import Blueprint, jsonify, request
from src.models.user import User, db
from functools import wraps
import jwt
import os

user_bp = Blueprint('user', __name__)

def token_required(f):
    """Decorator to require authentication token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({
                'success': False,
                'error': 'Token de acesso é obrigatório'
            }), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Verify token
            user = User.verify_token(token)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'Token inválido'
                }), 401
            
            # Add user to request context
            request.current_user = user
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': 'Token inválido'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated

@user_bp.route('/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username'):
            return jsonify({
                'success': False,
                'error': 'Nome de usuário é obrigatório'
            }), 400
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Email é obrigatório'
            }), 400
        
        if not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Senha é obrigatória'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            db.or_(User.username == data['username'], User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Usuário ou email já existe'
            }), 400
        
        # Create user
        user = User.create_from_dict(data)
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = user.generate_token()
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'token': token
            },
            'message': 'Usuário criado com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') and not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Nome de usuário ou email é obrigatório'
            }), 400
        
        if not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Senha é obrigatória'
            }), 400
        
        # Find user
        user = None
        if data.get('email'):
            user = User.query.filter_by(email=data['email']).first()
        elif data.get('username'):
            user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({
                'success': False,
                'error': 'Credenciais inválidas'
            }), 401
        
        if not user.active:
            return jsonify({
                'success': False,
                'error': 'Usuário desativado'
            }), 401
        
        # Update last login
        user.update_last_login()
        
        # Generate token
        token = user.generate_token()
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'token': token
            },
            'message': 'Login realizado com sucesso'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/auth/me', methods=['GET'])
@token_required
def get_current_user():
    """Get current user info"""
    try:
        return jsonify({
            'success': True,
            'data': request.current_user.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/auth/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (client-side token removal)"""
    return jsonify({
        'success': True,
        'message': 'Logout realizado com sucesso'
    })

@user_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """Get all users (admin only)"""
    try:
        if request.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        users = User.query.all()
        return jsonify({
            'success': True,
            'data': [user.to_dict() for user in users]
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/users', methods=['POST'])
@token_required
def create_user():
    """Create a new user (admin only)"""
    try:
        if request.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username'):
            return jsonify({
                'success': False,
                'error': 'Nome de usuário é obrigatório'
            }), 400
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'error': 'Email é obrigatório'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter(
            db.or_(User.username == data['username'], User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Usuário ou email já existe'
            }), 400
        
        # Create user
        user = User.create_from_dict(data)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': 'Usuário criado com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """Get a specific user"""
    try:
        # Users can only see their own profile unless they're admin
        if request.current_user.id != user_id and request.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """Update a user"""
    try:
        # Users can only update their own profile unless they're admin
        if request.current_user.id != user_id and request.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'username' in data:
            # Check if username is already taken
            existing = User.query.filter(User.username == data['username'], User.id != user_id).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Nome de usuário já existe'
                }), 400
            user.username = data['username']
        
        if 'email' in data:
            # Check if email is already taken
            existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing:
                return jsonify({
                    'success': False,
                    'error': 'Email já existe'
                }), 400
            user.email = data['email']
        
        if 'name' in data:
            user.name = data['name']
        if 'avatarUrl' in data:
            user.avatar_url = data['avatarUrl']
        if 'timezone' in data:
            user.timezone = data['timezone']
        if 'notificationsEnabled' in data:
            user.notifications_enabled = data['notificationsEnabled']
        
        # Only admin can change role and active status
        if request.current_user.role == 'admin':
            if 'role' in data:
                user.role = data['role']
            if 'active' in data:
                user.active = data['active']
        
        # Password change
        if 'password' in data:
            user.set_password(data['password'])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': user.to_dict(),
            'message': 'Usuário atualizado com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        if request.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': 'Acesso negado'
            }), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'Usuário não encontrado'
            }), 404
        
        # Don't allow deleting yourself
        if user.id == request.current_user.id:
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir seu próprio usuário'
            }), 400
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuário excluído com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

