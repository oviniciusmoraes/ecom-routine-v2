from flask import Blueprint, request, jsonify
from src.models.task import Task, DailyTaskSummary, db
from src.models.marketplace import Marketplace
from src.models.user import User
from datetime import datetime, timedelta, date
import uuid

task_bp = Blueprint('task', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    try:
        # Get query parameters
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        priority_filter = request.args.get('priority', 'all')
        marketplace_filter = request.args.get('marketplace', 'all')
        assignee_filter = request.args.get('assignee', 'all')
        date_filter = request.args.get('date', 'all')  # today, week, month, overdue
        
        # Build query
        query = Task.query
        
        # Apply filters
        if search:
            query = query.filter(
                db.or_(
                    Task.title.ilike(f'%{search}%'),
                    Task.description.ilike(f'%{search}%')
                )
            )
        
        if status_filter != 'all':
            query = query.filter(Task.status == status_filter)
        
        if priority_filter != 'all':
            query = query.filter(Task.priority == priority_filter)
        
        if marketplace_filter != 'all':
            query = query.filter(Task.marketplace_id == marketplace_filter)
        
        if assignee_filter != 'all':
            query = query.filter(Task.assignee_id == assignee_filter)
        
        # Date filters
        now = datetime.utcnow()
        if date_filter == 'today':
            today_start = datetime.combine(now.date(), datetime.min.time())
            today_end = datetime.combine(now.date(), datetime.max.time())
            query = query.filter(Task.due_date.between(today_start, today_end))
        elif date_filter == 'week':
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            query = query.filter(Task.due_date.between(week_start, week_end))
        elif date_filter == 'month':
            month_start = now.replace(day=1)
            next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
            query = query.filter(Task.due_date.between(month_start, next_month))
        elif date_filter == 'overdue':
            query = query.filter(Task.due_date < now, Task.status != 'completed')
        
        # Execute query
        tasks = query.order_by(Task.due_date.asc()).all()
        
        return jsonify({
            'success': True,
            'data': [task.to_dict() for task in tasks],
            'total': len(tasks)
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Título é obrigatório'
            }), 400
        
        if not data.get('marketplace'):
            return jsonify({
                'success': False,
                'error': 'Marketplace é obrigatório'
            }), 400
        
        # Generate ID if not provided
        if not data.get('id'):
            data['id'] = str(uuid.uuid4())
        
        # Validate marketplace exists
        marketplace = Marketplace.query.get(data['marketplace'])
        if not marketplace:
            return jsonify({
                'success': False,
                'error': 'Marketplace não encontrado'
            }), 400
        
        # Validate assignee if provided
        if data.get('assigneeId'):
            assignee = User.query.get(data['assigneeId'])
            if not assignee:
                return jsonify({
                    'success': False,
                    'error': 'Usuário responsável não encontrado'
                }), 400
        
        # Create task
        task = Task.create_from_dict(data)
        db.session.add(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': 'Tarefa criada com sucesso'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Tarefa não encontrada'
            }), 404
        
        return jsonify({
            'success': True,
            'data': task.to_dict()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Tarefa não encontrada'
            }), 404
        
        data = request.get_json()
        
        # Update fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
        if 'priority' in data:
            task.priority = data['priority']
        if 'category' in data:
            task.category = data['category']
        if 'marketplace' in data:
            task.marketplace_id = data['marketplace']
        if 'assigneeId' in data:
            task.assignee_id = data['assigneeId']
        if 'dueDate' in data:
            task.due_date = datetime.fromisoformat(data['dueDate']) if data['dueDate'] else None
        if 'estimatedTime' in data:
            task.estimated_time = data['estimatedTime']
        if 'links' in data:
            task.links = json.dumps(data['links'])
        if 'notes' in data:
            task.notes = data['notes']
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': 'Tarefa atualizada com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Tarefa não encontrada'
            }), 404
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tarefa excluída com sucesso'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/<task_id>/start', methods=['POST'])
def start_task(task_id):
    """Start a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Tarefa não encontrada'
            }), 404
        
        task.start_task()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': 'Tarefa iniciada'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/<task_id>/complete', methods=['POST'])
def complete_task(task_id):
    """Complete a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Tarefa não encontrada'
            }), 404
        
        task.complete_task()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': 'Tarefa concluída'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/<task_id>/pause', methods=['POST'])
def pause_task(task_id):
    """Pause a task"""
    try:
        task = Task.query.get(task_id)
        if not task:
            return jsonify({
                'success': False,
                'error': 'Tarefa não encontrada'
            }), 404
        
        task.pause_task()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': task.to_dict(),
            'message': 'Tarefa pausada'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/daily', methods=['GET'])
def get_daily_tasks():
    """Get today's tasks organized by status"""
    try:
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        # Get today's tasks
        tasks = Task.query.filter(
            Task.due_date.between(today_start, today_end)
        ).order_by(Task.due_date.asc()).all()
        
        # Organize by status
        organized_tasks = {
            'pending': [],
            'in_progress': [],
            'completed': [],
            'overdue': []
        }
        
        for task in tasks:
            if task.status == 'completed':
                organized_tasks['completed'].append(task.to_dict())
            elif task.status == 'in-progress':
                organized_tasks['in_progress'].append(task.to_dict())
            elif task.due_date < datetime.utcnow() and task.status != 'completed':
                organized_tasks['overdue'].append(task.to_dict())
            else:
                organized_tasks['pending'].append(task.to_dict())
        
        # Calculate progress
        total_tasks = len(tasks)
        completed_tasks = len(organized_tasks['completed'])
        progress = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        
        # Calculate remaining time
        remaining_time = sum([
            task.get('estimatedTime', 0) 
            for task in organized_tasks['pending'] + organized_tasks['in_progress']
        ])
        
        return jsonify({
            'success': True,
            'data': {
                'tasks': organized_tasks,
                'summary': {
                    'total': total_tasks,
                    'completed': completed_tasks,
                    'pending': len(organized_tasks['pending']),
                    'inProgress': len(organized_tasks['in_progress']),
                    'overdue': len(organized_tasks['overdue']),
                    'progress': progress,
                    'remainingTime': remaining_time
                },
                'date': today.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@task_bp.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    """Get task statistics"""
    try:
        # Overall stats
        total_tasks = Task.query.count()
        pending_tasks = Task.query.filter(Task.status.in_(['todo', 'in-progress'])).count()
        completed_tasks = Task.query.filter(Task.status == 'completed').count()
        overdue_tasks = Task.query.filter(
            Task.due_date < datetime.utcnow(),
            Task.status != 'completed'
        ).count()
        
        # Today's stats
        today = datetime.utcnow().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_tasks = Task.query.filter(
            Task.due_date.between(today_start, today_end)
        ).count()
        
        # Performance stats
        completion_rate = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1)
        
        return jsonify({
            'success': True,
            'data': {
                'totalTasks': total_tasks,
                'pendingTasks': pending_tasks,
                'completedTasks': completed_tasks,
                'overdueTasks': overdue_tasks,
                'todayTasks': today_tasks,
                'completionRate': completion_rate
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

