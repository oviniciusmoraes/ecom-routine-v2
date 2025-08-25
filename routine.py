from flask import Blueprint, request, jsonify
from src.models.routine import Routine, RoutineTask, db
from src.models.marketplace import Marketplace
from datetime import datetime, timedelta
import json

routine_bp = Blueprint('routine', __name__)

@routine_bp.route('/routines', methods=['GET'])
def get_routines():
    """Get all routines with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        frequency_filter = request.args.get('frequency', 'all')
        marketplace_filter = request.args.get('marketplace', 'all')
        
        # Build query
        query = Routine.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Routine.name.ilike(f'%{search}%'),
                    Routine.description.ilike(f'%{search}%')
                )
            )
        
        if status_filter != 'all':
            query = query.filter(Routine.status == status_filter)
        
        if frequency_filter != 'all':
            query = query.filter(Routine.frequency.ilike(f'%{frequency_filter}%'))
        
        if marketplace_filter != 'all':
            query = query.filter(Routine.marketplace_id == marketplace_filter)
        
        # Execute query
        routines = query.order_by(Routine.created_at.desc()).all()
        
        # Enrich with marketplace info
        result = []
        for routine in routines:
            routine_dict = routine.to_dict()
            marketplace = Marketplace.query.get(routine.marketplace_id)
            if marketplace:
                routine_dict['marketplaceName'] = marketplace.name
                routine_dict['marketplaceColor'] = marketplace.color
            result.append(routine_dict)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routine_bp.route('/routines', methods=['POST'])
def create_routine():
    """Create a new routine"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'Nome é obrigatório'
            }), 400
        
        if not data.get('marketplace'):
            return jsonify({
                'success': False,
                'error': 'Marketplace é obrigatório'
            }), 400
        
        if not data.get('frequency'):
            return jsonify({
                'success': False,
                'error': 'Frequência é obrigatória'
            }), 400
        
        # Validate marketplace exists
        marketplace = Marketplace.query.get(data['marketplace'])
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 400
        
        # Create routine
        routine = Routine.create_from_dict(data)
        db.session.add(routine)
        db.session.flush()  # Get the ID
        
        # Create routine tasks if provided
        if data.get('tasks'):
            for i, task_data in enumerate(data['tasks']):
                routine_task = RoutineTask(
                    routine_id=routine.id,
                    title=task_data.get('title'),
                    description=task_data.get('description'),
                    order=i,
                    estimated_time=task_data.get('estimatedTime'),
                    required=task_data.get('required', True),
                    task_type=task_data.get('taskType', 'manual'),
                    configuration=json.dumps(task_data.get('configuration', {}))
                )
                db.session.add(routine_task)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': routine.to_dict(),
            'message': 'Rotina criada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routine_bp.route('/routines/<int:routine_id>', methods=['GET'])
def get_routine(routine_id):
    """Get a specific routine"""
    try:
        routine = Routine.query.get(routine_id)
        if not routine:
            return jsonify({
                'success': False,
                'error': 'Rotina não encontrada'
            }), 404
        
        routine_dict = routine.to_dict()
        
        # Add marketplace info
        marketplace = Marketplace.query.get(routine.marketplace_id)
        if marketplace:
            routine_dict['marketplaceName'] = marketplace.name
            routine_dict['marketplaceColor'] = marketplace.color
        
        # Add routine tasks
        routine_dict['routineTasks'] = [task.to_dict() for task in routine.routine_tasks]
        
        return jsonify({
            'success': True,
            'data': routine_dict
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routine_bp.route('/routines/<int:routine_id>', methods=['PUT'])
def update_routine(routine_id):
    """Update a routine"""
    try:
        routine = Routine.query.get(routine_id)
        if not routine:
            return jsonify({
                'success': False,
                'error': 'Rotina não encontrada'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            routine.name = data['name']
        if 'description' in data:
            routine.description = data['description']
        if 'category' in data:
            routine.category = data['category']
        if 'priority' in data:
            routine.priority = data['priority']
        if 'marketplace' in data:
            routine.marketplace_id = data['marketplace']
        if 'frequency' in data:
            routine.frequency = data['frequency']
        if 'periodicityConfig' in data:
            routine.periodicity_config = json.dumps(data['periodicityConfig'])
        if 'estimatedTime' in data:
            routine.estimated_time = data['estimatedTime']
        if 'responsible' in data:
            routine.responsible = data['responsible']
        if 'status' in data:
            routine.status = data['status']
        if 'notificationsEnabled' in data:
            routine.notifications_enabled = data['notificationsEnabled']
        if 'nextExecution' in data:
            routine.next_execution = datetime.fromisoformat(data['nextExecution']) if data['nextExecution'] else None
        
        routine.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': routine.to_dict(),
            'message': 'Rotina atualizada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routine_bp.route('/routines/<int:routine_id>', methods=['DELETE'])
def delete_routine(routine_id):
    """Delete a routine"""
    try:
        routine = Routine.query.get(routine_id)
        if not routine:
            return jsonify({
                'success': False,
                'error': 'Rotina não encontrada'
            }), 404
        
        db.session.delete(routine)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Rotina excluída com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routine_bp.route('/routines/<int:routine_id>/execute', methods=['POST'])
def execute_routine(routine_id):
    """Execute a routine (create tasks from routine tasks)"""
    try:
        routine = Routine.query.get(routine_id)
        if not routine:
            return jsonify({
                'success': False,
                'error': 'Rotina não encontrada'
            }), 404
        
        from src.models.task import Task
        import uuid
        
        # Create tasks from routine tasks
        created_tasks = []
        for routine_task in routine.routine_tasks:
            task = Task(
                id=str(uuid.uuid4()),
                title=routine_task.title,
                description=routine_task.description,
                marketplace_id=routine.marketplace_id,
                routine_id=routine.id,
                category=routine.category,
                priority=routine.priority,
                estimated_time=routine_task.estimated_time,
                due_date=datetime.utcnow() + timedelta(hours=24)  # Default to 24 hours
            )
            db.session.add(task)
            created_tasks.append(task)
        
        # Update routine execution info
        routine.last_execution = datetime.utcnow()
        
        # Calculate next execution based on frequency
        if routine.frequency == 'daily':
            routine.next_execution = datetime.utcnow() + timedelta(days=1)
        elif routine.frequency == 'weekly':
            routine.next_execution = datetime.utcnow() + timedelta(weeks=1)
        elif routine.frequency == 'monthly':
            routine.next_execution = datetime.utcnow() + timedelta(days=30)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'routine': routine.to_dict(),
                'createdTasks': [task.to_dict() for task in created_tasks]
            },
            'message': f'Rotina executada com sucesso. {len(created_tasks)} tarefas criadas.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@routine_bp.route('/routines/stats', methods=['GET'])
def get_routine_stats():
    """Get routine statistics"""
    try:
        total_routines = Routine.query.count()
        active_routines = Routine.query.filter(Routine.status == 'active').count()
        
        # Today's executions (routines that should execute today)
        today = datetime.utcnow().date()
        today_executions = Routine.query.filter(
            Routine.next_execution >= datetime.combine(today, datetime.min.time()),
            Routine.next_execution < datetime.combine(today + timedelta(days=1), datetime.min.time())
        ).count()
        
        # Calculate completion rate (based on tasks created from routines)
        from src.models.task import Task
        routine_tasks = Task.query.filter(Task.routine_id.isnot(None)).all()
        completed_routine_tasks = [t for t in routine_tasks if t.status == 'completed']
        completion_rate = round((len(completed_routine_tasks) / len(routine_tasks) * 100) if routine_tasks else 0, 1)
        
        return jsonify({
            'success': True,
            'data': {
                'totalRoutines': total_routines,
                'activeRoutines': active_routines,
                'todayExecutions': today_executions,
                'completionRate': completion_rate
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

