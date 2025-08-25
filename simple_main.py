import os
import sys
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app, origins="*")

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Simple User model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(200))
    avatar_url = db.Column(db.String(500))
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    timezone = db.Column(db.String(50), default='America/Sao_Paulo')
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_initials(self):
        if self.name:
            parts = self.name.split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            else:
                return parts[0][:2].upper()
        else:
            return self.username[:2].upper()
    
    def generate_token(self):
        payload = {
            'user_id': self.id,
            'username': self.username,
            'exp': datetime.utcnow().timestamp() + 86400
        }
        return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            return user
        except:
            return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'avatarUrl': self.avatar_url,
            'role': self.role,
            'active': self.active,
            'timezone': self.timezone,
            'notificationsEnabled': self.notifications_enabled,
            'initials': self.get_initials(),
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'lastLogin': self.last_login.isoformat() if self.last_login else None
        }

# Simple Marketplace model
class Marketplace(db.Model):
    __tablename__ = 'marketplaces'
    
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(7), default='#3B82F6')
    logo_url = db.Column(db.String(500))
    type = db.Column(db.String(50), nullable=False)
    priority = db.Column(db.String(20), default='medium')
    tags = db.Column(db.Text)  # JSON string
    responsible = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    favorite = db.Column(db.Boolean, default=False)
    admin_url = db.Column(db.String(500))
    reports_url = db.Column(db.String(500))
    other_url = db.Column(db.String(500))
    schedule_start = db.Column(db.String(5))
    schedule_end = db.Column(db.String(5))
    timezone = db.Column(db.String(50), default='America/Sao_Paulo')
    custom_fields = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'color': self.color,
            'logoUrl': self.logo_url,
            'type': self.type,
            'priority': self.priority,
            'tags': json.loads(self.tags) if self.tags else [],
            'responsible': self.responsible,
            'active': self.active,
            'favorite': self.favorite,
            'urls': {
                'admin': self.admin_url,
                'reports': self.reports_url,
                'other': self.other_url
            },
            'schedule': {
                'start': self.schedule_start,
                'end': self.schedule_end
            },
            'timezone': self.timezone,
            'customFields': json.loads(self.custom_fields) if self.custom_fields else [],
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'weeklyTasks': {
                'total': 0,
                'completed': 0,
                'pending': 0
            }
        }

# Authentication routes
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') and not data.get('email'):
            return jsonify({'success': False, 'error': 'Nome de usuário ou email é obrigatório'}), 400
        
        if not data.get('password'):
            return jsonify({'success': False, 'error': 'Senha é obrigatória'}), 400
        
        user = None
        if data.get('email'):
            user = User.query.filter_by(email=data['email']).first()
        elif data.get('username'):
            user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'success': False, 'error': 'Credenciais inválidas'}), 401
        
        if not user.active:
            return jsonify({'success': False, 'error': 'Usuário desativado'}), 401
        
        user.last_login = datetime.utcnow()
        db.session.commit()
        
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
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data.get('username'):
            return jsonify({'success': False, 'error': 'Nome de usuário é obrigatório'}), 400
        
        if not data.get('email'):
            return jsonify({'success': False, 'error': 'Email é obrigatório'}), 400
        
        if not data.get('password'):
            return jsonify({'success': False, 'error': 'Senha é obrigatória'}), 400
        
        existing_user = User.query.filter(
            db.or_(User.username == data['username'], User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'success': False, 'error': 'Usuário ou email já existe'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            name=data.get('name'),
            role='user'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
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
        return jsonify({'success': False, 'error': str(e)}), 500

# Marketplace routes
@app.route('/api/marketplaces', methods=['GET'])
def get_marketplaces():
    try:
        marketplaces = Marketplace.query.all()
        return jsonify({
            'success': True,
            'data': [marketplace.to_dict() for marketplace in marketplaces],
            'total': len(marketplaces)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/marketplaces', methods=['POST'])
def create_marketplace():
    try:
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Nome é obrigatório'}), 400
        
        if not data.get('type'):
            return jsonify({'success': False, 'error': 'Tipo é obrigatório'}), 400
        
        marketplace = Marketplace(
            id=data.get('id', f"marketplace-{datetime.utcnow().timestamp()}"),
            name=data['name'],
            description=data.get('description'),
            color=data.get('color', '#3B82F6'),
            logo_url=data.get('logoUrl'),
            type=data['type'],
            priority=data.get('priority', 'medium'),
            tags=json.dumps(data.get('tags', [])),
            responsible=data.get('responsible'),
            active=data.get('active', True),
            favorite=data.get('favorite', False),
            admin_url=data.get('urls', {}).get('admin'),
            reports_url=data.get('urls', {}).get('reports'),
            other_url=data.get('urls', {}).get('other'),
            schedule_start=data.get('schedule', {}).get('start'),
            schedule_end=data.get('schedule', {}).get('end'),
            timezone=data.get('timezone', 'America/Sao_Paulo'),
            custom_fields=json.dumps(data.get('customFields', []))
        )
        
        db.session.add(marketplace)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': marketplace.to_dict(),
            'message': 'Marketplace criado com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# Serve static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

# Initialize database and create sample data
with app.app_context():
    db.create_all()
    
    # Create sample admin user if no users exist
    if User.query.count() == 0:
        admin_user = User(
            username='admin',
            email='admin@ecomroutine.com',
            name='Administrador',
            role='admin',
            active=True
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        regular_user = User(
            username='joao',
            email='joao@ecomroutine.com',
            name='João Silva',
            role='user',
            active=True
        )
        regular_user.set_password('123456')
        db.session.add(regular_user)
        
        db.session.commit()
        print("Sample users created:")
        print("Admin: admin / admin123")
        print("User: joao / 123456")
    
    # Create sample marketplaces if none exist
    if Marketplace.query.count() == 0:
        sample_marketplaces = [
            {
                'id': 'mercado-livre-matriz',
                'name': 'Mercado Livre Matriz',
                'description': 'Conta principal do Mercado Livre para produtos principais',
                'color': '#3483FA',
                'type': 'ecommerce',
                'priority': 'high',
                'tags': json.dumps(['e-commerce', 'principal', 'nacional']),
                'responsible': 'João Silva',
                'active': True,
                'favorite': True,
                'admin_url': 'https://vendas.mercadolivre.com.br',
                'schedule_start': '08:00',
                'schedule_end': '18:00',
                'timezone': 'America/Sao_Paulo'
            },
            {
                'id': 'shopee-filial',
                'name': 'Shopee Filial',
                'description': 'Conta filial da Shopee para produtos específicos',
                'color': '#EE4D2D',
                'type': 'ecommerce',
                'priority': 'medium',
                'tags': json.dumps(['e-commerce', 'mobile', 'internacional']),
                'responsible': 'Maria Santos',
                'active': True,
                'favorite': False,
                'admin_url': 'https://seller.shopee.com.br',
                'schedule_start': '09:00',
                'schedule_end': '17:00',
                'timezone': 'America/Sao_Paulo'
            },
            {
                'id': 'amazon-br',
                'name': 'Amazon Brasil',
                'description': 'Marketplace Amazon para o mercado brasileiro',
                'color': '#FF9900',
                'type': 'ecommerce',
                'priority': 'high',
                'tags': json.dumps(['premium', 'logística', 'nacional']),
                'responsible': 'Pedro Oliveira',
                'active': True,
                'favorite': True,
                'admin_url': 'https://sellercentral.amazon.com.br',
                'schedule_start': '08:00',
                'schedule_end': '20:00',
                'timezone': 'America/Sao_Paulo'
            }
        ]
        
        for marketplace_data in sample_marketplaces:
            marketplace = Marketplace(**marketplace_data)
            db.session.add(marketplace)
        
        db.session.commit()
        print("Sample marketplaces created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

