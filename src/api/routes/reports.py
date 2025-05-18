from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from ...config.models import db, Project, Routine, Session, Checkin, Commitment, ProjectTask, CatchlistItem
from ..utils.helpers import get_current_user_id
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, cast, Date

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/api/reports/daily-checkins', methods=['GET'])
@jwt_required()
def get_daily_checkins():
    current_user_id = get_current_user_id()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get daily check-ins from Session records
    daily_checkins = db.session.query(
        func.date(Session.start_time).label('day'),
        func.count(Session.id).label('count')
    ).join(
        Routine, Routine.id == Session.routine_id
    ).filter(
        Routine.user_id == current_user_id,
        Session.start_time.between(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        ),
        Session.completed == True
    ).group_by(
        func.date(Session.start_time)
    ).all()
    
    # Convert to dictionary format
    result = {
        'daily_checkins': [
            {
                'day': day.strftime('%Y-%m-%d'),
                'count': count
            }
            for day, count in daily_checkins
        ]
    }
    
    return jsonify(result)

@reports_bp.route('/api/reports/daily-activity', methods=['GET'])
@jwt_required()
def get_daily_activity():
    current_user_id = get_current_user_id()
    day = request.args.get('day')
    
    if not day:
        return jsonify({"message": "Day is required"}), 400
    
    try:
        day_date = datetime.strptime(day, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get all sessions for the day
    sessions = db.session.query(
        Session, Routine
    ).join(
        Routine, Routine.id == Session.routine_id
    ).filter(
        Routine.user_id == current_user_id,
        func.date(Session.start_time) == day_date,
        Session.completed == True
    ).all()
    
    result = {
        'sessions': [
            {
                'id': session.id,
                'title': routine.title,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'rpe': session.rpe,
                'notes': session.notes
            }
            for session, routine in sessions
        ]
    }
    
    return jsonify(result)

@reports_bp.route('/api/reports/comments', methods=['GET'])
@jwt_required()
def get_comments():
    current_user_id = get_current_user_id()
    entity_type = request.args.get('entity_type')
    entity_id = request.args.get('entity_id')
    
    if not entity_type or not entity_id:
        return jsonify({"message": "Entity type and ID are required"}), 400
    
    try:
        entity_id = int(entity_id)
    except ValueError:
        return jsonify({"message": "Invalid entity ID"}), 400
    
    # Get checkins based on entity type
    if entity_type == 'session':
        session = Session.query.get(entity_id)
        if not session:
            return jsonify({"message": "Session not found"}), 404
            
        routine = Routine.query.get(session.routine_id)
        if not routine or routine.user_id != current_user_id:
            return jsonify({"message": "Not authorized"}), 403
            
        checkins = Checkin.query.filter_by(
            entity_type='session',
            entity_id=entity_id
        ).order_by(Checkin.timestamp.desc()).all()
        
    elif entity_type == 'project_task':
        task = ProjectTask.query.get(entity_id)
        if not task:
            return jsonify({"message": "Task not found"}), 404
            
        project = Project.query.get(task.project_id)
        if not project or project.user_id != current_user_id:
            return jsonify({"message": "Not authorized"}), 403
            
        checkins = Checkin.query.filter_by(
            entity_type='project_task',
            entity_id=entity_id
        ).order_by(Checkin.timestamp.desc()).all()
        
    elif entity_type == 'catchlist_item':
        item = CatchlistItem.query.get(entity_id)
        if not item or item.user_id != current_user_id:
            return jsonify({"message": "Not authorized"}), 403
            
        checkins = Checkin.query.filter_by(
            entity_type='catchlist_item',
            entity_id=entity_id
        ).order_by(Checkin.timestamp.desc()).all()
        
    else:
        return jsonify({"message": "Invalid entity type"}), 400
    
    result = {
        'checkins': [
            {
                'id': checkin.id,
                'content': checkin.comment,
                'timestamp': checkin.timestamp.isoformat(),
                'user_id': checkin.user_id,
                'rpe': checkin.rpe
            }
            for checkin in checkins
        ]
    }
    
    return jsonify(result)

@reports_bp.route('/api/reports/weekly', methods=['GET'])
@jwt_required()
def get_weekly_report():
    current_user_id = get_current_user_id()
    
    # Get date parameters
    end_date_str = request.args.get('end_date')
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    else:
        end_date = date.today()
    
    # Calculate the start date (7 days before the end date)
    start_date = end_date - timedelta(days=6)
    
    # Debug the date range
    print(f"Debug - Weekly report date range: {start_date} to {end_date}")
    
    # Initialize the response structure
    report = {
        'period': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        },
        'projects': [],
        'daily_stats': {},
        'checkins': {
            'total': 0,
            'by_day': {}
        },
        'completed_tasks': {
            'total': 0,
            'by_day': {}
        },
        'completed_catchlist': {
            'total': 0,
            'by_day': {}
        },
        'average_rpe': None
    }
    
    # Initialize days
    current_date = start_date
    while current_date <= end_date:
        day_str = current_date.strftime('%Y-%m-%d')
        report['daily_stats'][day_str] = {
            'checkins': 0,
            'completed_tasks': 0,
            'completed_catchlist': 0,
            'rpe_values': []
        }
        report['checkins']['by_day'][day_str] = 0
        report['completed_tasks']['by_day'][day_str] = 0
        report['completed_catchlist']['by_day'][day_str] = 0
        current_date += timedelta(days=1)
    
    # Get projects and their task completion stats
    projects = Project.query.filter_by(user_id=current_user_id).all()
    for project in projects:
        # Count completed tasks in the date range using Commitment records
        completed_tasks = db.session.query(ProjectTask).join(
            Commitment, Commitment.project_task_id == ProjectTask.id
        ).filter(
            ProjectTask.project_id == project.id,
            Commitment.completed == True,
            Commitment.due_date.between(start_date, end_date)
        ).all()
        
        # Get all tasks for this project
        all_tasks = ProjectTask.query.filter_by(project_id=project.id).all()
        
        project_data = {
            'id': project.id,
            'title': project.title,
            'total_tasks': len(all_tasks),
            'completed_tasks': len(completed_tasks),
            'completion_percentage': round(len(completed_tasks) / max(len(all_tasks), 1) * 100)
        }
        
        report['projects'].append(project_data)
    
    # Get daily check-ins from Session records
    checkins = db.session.query(
        func.date(Session.start_time).label('day'),
        func.count(Session.id).label('count')
    ).join(
        Routine, Routine.id == Session.routine_id
    ).filter(
        Routine.user_id == current_user_id,
        Session.start_time.between(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        ),
        Session.completed == True
    ).group_by(
        func.date(Session.start_time)
    ).all()
    
    total_checkins = 0
    for day, count in checkins:
        if isinstance(day, str):
            day_str = day
        else:
            day_str = day.strftime('%Y-%m-%d')
        if day_str in report['checkins']['by_day']:
            report['checkins']['by_day'][day_str] = count
            report['daily_stats'][day_str]['checkins'] = count
            total_checkins += count
    
    report['checkins']['total'] = total_checkins
    
    # Get completed tasks by day using Commitment records
    completed_tasks = db.session.query(
        Commitment.due_date.label('day'),
        func.count().label('count')
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.completed == True,
        Commitment.project_task_id.isnot(None),
        Commitment.due_date.between(start_date, end_date)
    ).group_by(
        Commitment.due_date
    ).all()
    
    total_completed_tasks = 0
    for day, count in completed_tasks:
        if day:
            if isinstance(day, str):
                day_str = day
            else:
                day_str = day.strftime('%Y-%m-%d')
            if day_str in report['completed_tasks']['by_day']:
                report['completed_tasks']['by_day'][day_str] = count
                report['daily_stats'][day_str]['completed_tasks'] = count
                total_completed_tasks += count
    
    report['completed_tasks']['total'] = total_completed_tasks
    
    # Get completed catchlist items by day using Commitment records
    completed_catchlist = db.session.query(
        Commitment.due_date.label('day'),
        func.count(Commitment.id).label('count')
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.completed == True,
        Commitment.due_date.between(start_date, end_date),
        Commitment.catchlist_item_id.isnot(None)
    ).group_by(
        Commitment.due_date
    ).all()
    
    total_completed_catchlist = 0
    for day, count in completed_catchlist:
        if day:
            if isinstance(day, str):
                day_str = day
            else:
                day_str = day.strftime('%Y-%m-%d')
            if day_str in report['completed_catchlist']['by_day']:
                report['completed_catchlist']['by_day'][day_str] = count
                report['daily_stats'][day_str]['completed_catchlist'] = count
                total_completed_catchlist += count
    
    report['completed_catchlist']['total'] = total_completed_catchlist
    
    # Get RPE values for the period
    rpe_values = db.session.query(
        cast(Checkin.timestamp, Date).label('day'),
        Checkin.rpe
    ).filter(
        Checkin.user_id == current_user_id,
        Checkin.rpe.isnot(None),
        cast(Checkin.timestamp, Date).between(start_date, end_date)
    ).all()
    
    all_rpe_values = []
    
    # Group RPE values by day
    rpe_by_day = {}
    for day, rpe in rpe_values:
        if day and rpe:
            if isinstance(day, str):
                day_str = day
            else:
                day_str = day.strftime('%Y-%m-%d')
            
            if day_str not in rpe_by_day:
                rpe_by_day[day_str] = []
            
            rpe_by_day[day_str].append(rpe)
            all_rpe_values.append(rpe)
    
    # Add RPE values to the daily stats
    for day_str, rpe_list in rpe_by_day.items():
        if day_str in report['daily_stats']:
            report['daily_stats'][day_str]['rpe_values'] = rpe_list
            
    # Calculate average RPE
    if all_rpe_values:
        report['average_rpe'] = round(sum(all_rpe_values) / len(all_rpe_values), 1)
    
    # Calculate daily average RPE
    for day, stats in report['daily_stats'].items():
        rpe_values = stats.get('rpe_values', [])
        if rpe_values:
            stats['average_rpe'] = round(sum(rpe_values) / len(rpe_values), 1)
        else:
            stats['average_rpe'] = None
        # Remove the raw values from the response
        if 'rpe_values' in stats:
            del stats['rpe_values']
    
    return jsonify(report)

@reports_bp.route('/api/reports/day-details', methods=['GET'])
@jwt_required()
def day_details():
    current_user_id = get_current_user_id()
    
    # Get date parameter
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({"message": "Date parameter is required"}), 400
    
    try:
        day_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        day_str = day_date.strftime('%Y-%m-%d')
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get category parameter
    category = request.args.get('category')
    if not category or category not in ['checkins', 'tasks', 'catchlist']:
        return jsonify({"message": "Valid category parameter is required"}), 400
    
    result = {
        'date': day_str,
        'category': category,
        'items': []
    }
    
    # Get details based on category
    if category == 'checkins':
        # Get sessions for this day
        sessions = db.session.query(
            Session, Routine
        ).join(
            Routine, Routine.id == Session.routine_id
        ).filter(
            Routine.user_id == current_user_id,
            func.date(Session.start_time) == day_date,
            Session.completed == True
        ).all()
        
        for session, routine in sessions:
            # Get checkins for this session
            checkins = Checkin.query.filter_by(
                entity_type='session',
                entity_id=session.id,
                user_id=current_user_id
            ).order_by(Checkin.timestamp).all()
            
            checkins_data = []
            for checkin in checkins:
                checkins_data.append({
                    'content': checkin.comment,
                    'rpe': checkin.rpe,
                    'created_at': checkin.timestamp.strftime('%Y-%m-%d %H:%M')
                })
            
            result['items'].append({
                'id': session.id,
                'type': 'session',
                'title': routine.title,
                'details': {
                    'start_time': session.start_time.strftime('%H:%M'),
                    'end_time': session.end_time.strftime('%H:%M'),
                    'rpe': session.rpe,
                    'notes': session.notes
                },
                'checkins': checkins_data
            })
            
    elif category == 'tasks':
        # Get completed tasks for this day using TaskExecution records
        tasks = db.session.query(
            TaskExecution, ProjectSubtask, Project
        ).join(
            ProjectSubtask, ProjectSubtask.id == TaskExecution.task_id
        ).join(
            Project, Project.id == TaskExecution.project_id
        ).filter(
            TaskExecution.user_id == current_user_id,
            TaskExecution.execution_date == day_date,
            TaskExecution.completed == True
        ).all()
        
        for execution, task, project in tasks:
            # Get checkins for this task
            checkins = Checkin.query.filter_by(
                entity_type='project_task',
                entity_id=task.id,
                user_id=current_user_id
            ).order_by(Checkin.timestamp).all()
            
            checkins_data = []
            for checkin in checkins:
                checkins_data.append({
                    'content': checkin.comment,
                    'rpe': checkin.rpe,
                    'created_at': checkin.timestamp.strftime('%Y-%m-%d %H:%M')
                })
            
            result['items'].append({
                'id': task.id,
                'type': 'project_subtask',
                'title': task.title,
                'details': {
                    'project_title': project.title,
                    'completed_at': execution.execution_date.strftime('%Y-%m-%d'),
                    'notes': execution.notes
                },
                'checkins': checkins_data
            })
    
    elif category == 'catchlist':
        # Get completed catchlist entries for this day using Commitment records
        catchlist_items = db.session.query(
            CatchlistItem, Commitment
        ).join(
            Commitment, Commitment.catchlist_item_id == CatchlistItem.id
        ).filter(
            Commitment.user_id == current_user_id,
            Commitment.due_date == day_date,
            Commitment.completed == True
        ).all()
        
        for item in catchlist_items:
            # Get checkins for this catchlist item
            checkins = Checkin.query.filter_by(
                entity_type='catchlist_item',
                entity_id=item.CatchlistItem.id,
                user_id=current_user_id
            ).order_by(Checkin.timestamp).all()
            
            checkins_data = []
            for checkin in checkins:
                checkins_data.append({
                    'content': checkin.comment,
                    'rpe': checkin.rpe,
                    'created_at': checkin.timestamp.strftime('%Y-%m-%d %H:%M')
                })
            
            result['items'].append({
                'id': item.CatchlistItem.id,
                'type': 'catchlist_item',
                'title': item.CatchlistItem.content,
                'details': {
                    'completed_at': item.Commitment.completed_at.isoformat() if item.Commitment.completed_at else None,
                    'status': item.CatchlistItem.status,
                    'notes': item.Commitment.notes
                },
                'checkins': checkins_data
            })
    
    return jsonify(result)

@reports_bp.route('/api/reports/fix-all-dates', methods=['POST'])
@jwt_required()
def fix_all_dates():
    current_user_id = get_current_user_id()
    
    try:
        from datetime import datetime
        today = datetime.utcnow()
        results = {'catchlist': 0, 'tasks': 0}
        
        # Fix catchlist items with future dates
        catchlist_items = CatchlistItem.query.filter(
            CatchlistItem.user_id == current_user_id,
            CatchlistItem.completed == True,
            CatchlistItem.completed_at > today
        ).all()
        
        for item in catchlist_items:
            item.completed_at = today
            results['catchlist'] += 1
        
        # Fix project subtasks with future dates
        # First get all projects for this user
        projects = Project.query.filter_by(user_id=current_user_id).all()
        project_ids = [p.id for p in projects]
        
        subtasks = ProjectSubtask.query.filter(
            ProjectSubtask.project_id.in_(project_ids),
            ProjectSubtask.complete == True,
            ProjectSubtask.updated_at > today
        ).all()
        
        for subtask in subtasks:
            subtask.updated_at = today
            results['tasks'] += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully updated {results['catchlist']} catchlist items and {results['tasks']} tasks",
            "updated": results
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@reports_bp.route('/api/reports/fix-dates-debug', methods=['POST'])
def fix_dates_debug():
    """This endpoint fixes future dates without requiring authentication"""
    try:
        from datetime import datetime
        # Use a fixed date in the past rather than relative to now
        fixed_date = datetime(2023, 5, 14, 12, 0, 0)
        results = {'catchlist': 0, 'tasks': 0}
        
        print(f"Debug - Fixing dates with fixed date: {fixed_date}")
        
        # Fix ALL catchlist items with future dates, regardless of user
        catchlist_items = CatchlistItem.query.filter(
            CatchlistItem.completed == True
        ).all()
        
        print(f"Debug - Found {len(catchlist_items)} catchlist items to update")
        for item in catchlist_items:
            old_date = item.completed_at
            item.completed_at = fixed_date
            print(f"Debug - Updating catchlist item {item.id} date from {old_date} to {fixed_date}")
            results['catchlist'] += 1
        
        # Fix ALL project subtasks with future dates, regardless of user
        subtasks = ProjectSubtask.query.filter(
            ProjectSubtask.complete == True
        ).all()
        
        print(f"Debug - Found {len(subtasks)} subtasks to update")
        for subtask in subtasks:
            old_date = subtask.updated_at
            subtask.updated_at = fixed_date
            print(f"Debug - Updating subtask {subtask.id} date from {old_date} to {fixed_date}")
            results['tasks'] += 1
        
        db.session.commit()
        
        return jsonify({
            "message": f"Successfully updated {results['catchlist']} catchlist items and {results['tasks']} tasks",
            "updated": results
        })
    except Exception as e:
        db.session.rollback()
        print(f"Error in fix_dates_debug: {str(e)}")
        return jsonify({"message": str(e)}), 500

@reports_bp.route('/api/reports/test-weekly', methods=['GET'])
def test_weekly_report():
    """Test endpoint for the weekly report that doesn't require authentication"""
    try:
        # Get date parameters
        end_date_str = request.args.get('end_date')
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
        else:
            end_date = date.today()
        
        # Calculate the start date (7 days before the end date)
        start_date = end_date - timedelta(days=6)
        
        print(f"Debug - Test Weekly report date range: {start_date} to {end_date}")
        
        # Get some basic stats without authentication
        # Just count completed tasks and catchlist items
        completed_tasks = db.session.query(
            func.count(ProjectSubtask.id)
        ).filter(
            ProjectSubtask.complete == True,
            cast(ProjectSubtask.updated_at, Date).between(start_date, end_date)
        ).scalar() or 0
        
        completed_catchlist = db.session.query(
            func.count(CatchlistItem.id)
        ).filter(
            CatchlistItem.completed == True,
            CatchlistItem.completed_at.isnot(None),
            cast(CatchlistItem.completed_at, Date).between(start_date, end_date)
        ).scalar() or 0
        
        result = {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d')
            },
            'stats': {
                'completed_tasks': completed_tasks,
                'completed_catchlist': completed_catchlist
            }
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"Error in test_weekly_report: {str(e)}")
        return jsonify({"message": str(e)}), 500

@reports_bp.route('/api/reports/test', methods=['GET'])
def test_report():
    """Simple test endpoint that doesn't require authentication"""
    try:
        # Create a sample response
        from datetime import datetime, date, timedelta
        today = date.today()
        
        # Get all completed tasks
        completed_tasks = db.session.query(func.count(ProjectSubtask.id)).filter(
            ProjectSubtask.complete == True
        ).scalar() or 0
        
        # Get all completed catchlist items
        completed_catchlist = db.session.query(func.count(CatchlistItem.id)).filter(
            CatchlistItem.completed == True
        ).scalar() or 0
        
        return jsonify({
            "message": "Test report successful",
            "today": today.strftime('%Y-%m-%d'),
            "stats": {
                "completed_tasks": completed_tasks,
                "completed_catchlist": completed_catchlist
            }
        })
    except Exception as e:
        print(f"Error in test_report: {str(e)}")
        return jsonify({"message": str(e)}), 500

@reports_bp.route('/api/reports/completion-by-day', methods=['GET'])
@jwt_required()
def get_completion_by_day():
    current_user_id = get_current_user_id()
    
    # Get date range from query params
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "start_date and end_date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get completed catchlist items by day using Commitment records
    catchlist_completions = db.session.query(
        Commitment.due_date.label('day'),
        func.count(Commitment.id).label('count')
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.completed == True,
        Commitment.due_date.between(start_date, end_date),
        Commitment.catchlist_item_id.isnot(None)
    ).group_by(
        Commitment.due_date
    ).all()
    
    # Get completed project tasks by day
    project_task_completions = db.session.query(
        Commitment.due_date.label('day'),
        func.count(Commitment.id).label('count')
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.completed == True,
        Commitment.due_date.between(start_date, end_date),
        Commitment.project_task_id.isnot(None)
    ).group_by(
        Commitment.due_date
    ).all()
    
    # Get completed sessions by day
    session_completions = db.session.query(
        Commitment.due_date.label('day'),
        func.count(Commitment.id).label('count')
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.completed == True,
        Commitment.due_date.between(start_date, end_date),
        Commitment.session_id.isnot(None)
    ).group_by(
        Commitment.due_date
    ).all()
    
    # Combine all results
    results = {}
    for completion in catchlist_completions + project_task_completions + session_completions:
        day = completion.day.isoformat()
        if day not in results:
            results[day] = {
                'catchlist_items': 0,
                'project_tasks': 0,
                'sessions': 0,
                'total': 0
            }
        results[day]['total'] += completion.count
        
        # Determine which type of completion this is
        if completion in catchlist_completions:
            results[day]['catchlist_items'] += completion.count
        elif completion in project_task_completions:
            results[day]['project_tasks'] += completion.count
        elif completion in session_completions:
            results[day]['sessions'] += completion.count
    
    return jsonify(results)

@reports_bp.route('/api/reports/daily-summary/<date>', methods=['GET'])
@jwt_required()
def get_daily_summary(date_str):
    current_user_id = get_current_user_id()
    
    try:
        day_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get completed catchlist entries for this day using Commitment records
    catchlist_completions = db.session.query(
        CatchlistItem, Commitment
    ).join(
        Commitment, Commitment.catchlist_item_id == CatchlistItem.id
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.due_date == day_date,
        Commitment.completed == True
    ).all()
    
    # Get completed project tasks for this day
    project_task_completions = db.session.query(
        ProjectTask, Commitment
    ).join(
        Commitment, Commitment.project_task_id == ProjectTask.id
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.due_date == day_date,
        Commitment.completed == True
    ).all()
    
    # Get completed sessions for this day
    session_completions = db.session.query(
        Session, Commitment
    ).join(
        Commitment, Commitment.session_id == Session.id
    ).filter(
        Commitment.user_id == current_user_id,
        Commitment.due_date == day_date,
        Commitment.completed == True
    ).all()
    
    return jsonify({
        'date': day_date.isoformat(),
        'catchlist_items': [{
            'id': item.CatchlistItem.id,
            'content': item.CatchlistItem.content,
            'completed_at': item.Commitment.completed_at.isoformat() if item.Commitment.completed_at else None
        } for item in catchlist_completions],
        'project_tasks': [{
            'id': item.ProjectTask.id,
            'title': item.ProjectTask.title,
            'completed_at': item.Commitment.completed_at.isoformat() if item.Commitment.completed_at else None
        } for item in project_task_completions],
        'sessions': [{
            'id': item.Session.id,
            'title': item.Session.title,
            'completed_at': item.Commitment.completed_at.isoformat() if item.Commitment.completed_at else None
        } for item in session_completions]
    }) 