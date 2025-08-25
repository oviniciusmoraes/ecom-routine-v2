import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Import models after db initialization
from src.models.user import User
from src.models.marketplace import Marketplace
from src.models.routine import Routine, RoutineTask
from src.models.task import Task, DailyTaskSummary

# Import routes
from src.routes.user import user_bp
from src.routes.marketplace import marketplace_bp
from src.routes.routine import routine_bp
from src.routes.task import task_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Enable CORS for all routes
CORS(app, origins="*")

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(marketplace_bp, url_prefix='/api')
app.register_blueprint(routine_bp, url_prefix='/api')
app.register_blueprint(task_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize db with app
db.init_app(app)

# Update all model files to use this db instance
User.metadata.bind = db.engine
Marketplace.metadata.bind = db.engine
Routine.metadata.bind = db.engine
RoutineTask.metadata.bind = db.engine
Task.metadata.bind = db.engine
DailyTaskSummary.metadata.bind = db.engine

# Initialize database and create sample data
with app.app_context():
    db.create_all()
    
    # Create sample admin user if no users exist
    from src.models.user import User
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
        
        # Create sample regular user
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
    from src.models.marketplace import Marketplace
    if Marketplace.query.count() == 0:
        import json
        
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
    
    # Create sample routines if none exist
    from src.models.routine import Routine, RoutineTask
    if Routine.query.count() == 0:
        import json
        from datetime import datetime, timedelta
        
        sample_routines = [
            {
                'name': 'Verificação Diária Shopee',
                'description': 'Análise diária de métricas e verificação de anormalidades',
                'category': 'Monitoramento',
                'priority': 'high',
                'marketplace_id': 'shopee-filial',
                'frequency': 'daily',
                'periodicity_config': json.dumps({'time': '09:00'}),
                'estimated_time': 45,
                'responsible': 'João Silva',
                'status': 'active',
                'next_execution': datetime.utcnow() + timedelta(days=1)
            },
            {
                'name': 'Análise Semanal ML',
                'description': 'Comparação de métricas e otimização de anúncios',
                'category': 'Análise',
                'priority': 'medium',
                'marketplace_id': 'mercado-livre-matriz',
                'frequency': 'weekly',
                'periodicity_config': json.dumps({'day': 'monday', 'time': '10:00'}),
                'estimated_time': 150,
                'responsible': 'Maria Santos',
                'status': 'active',
                'next_execution': datetime.utcnow() + timedelta(days=7)
            }
        ]
        
        for routine_data in sample_routines:
            routine = Routine(**routine_data)
            db.session.add(routine)
            db.session.flush()  # Get the ID
            
            # Add sample tasks for each routine
            if routine.name == 'Verificação Diária Shopee':
                tasks = [
                    {
                        'routine_id': routine.id,
                        'title': 'Verificar página inicial - anormalidades',
                        'description': 'Análise de picos anômalos de pedidos e verificação geral',
                        'order': 0,
                        'estimated_time': 10,
                        'required': True,
                        'task_type': 'manual'
                    },
                    {
                        'routine_id': routine.id,
                        'title': 'Tratar pedidos atrasados',
                        'description': 'Resolver pendências e garantir zero atrasos',
                        'order': 1,
                        'estimated_time': 20,
                        'required': True,
                        'task_type': 'manual'
                    },
                    {
                        'routine_id': routine.id,
                        'title': 'Analisar métricas de saúde da conta',
                        'description': 'Verificar indicadores e garantir que estão em verde',
                        'order': 2,
                        'estimated_time': 15,
                        'required': True,
                        'task_type': 'manual'
                    }
                ]
                
                for task_data in tasks:
                    routine_task = RoutineTask(**task_data)
                    db.session.add(routine_task)
        
        db.session.commit()
        print("Sample routines created")

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

@app.errorhandler(404)
def not_found(error):
    return {'success': False, 'error': 'Endpoint não encontrado'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'success': False, 'error': 'Erro interno do servidor'}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

