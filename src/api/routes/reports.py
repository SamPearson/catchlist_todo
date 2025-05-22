from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import db, Project, Routine, Session, Checkin, Commitment, ProjectTask, CatchlistItem, ReportGenerator, DayBlock, WeekBlock, MonthBlock, SeasonBlock, YearBlock
from ..utils.helpers import get_current_user_id
from datetime import datetime, date, timedelta
from sqlalchemy import func, and_, cast, Date
from ...config.models.time_blocks import DayBlock, WeekBlock, MonthBlock, SeasonBlock

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

@reports_bp.route('/api/reports/weekly-report/<end_date>', methods=['GET'])
@jwt_required()
def get_weekly_report(end_date):
    """Get weekly report data"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    try:
        report_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Calculate the start date (7 days before the end date)
    start_date = report_date - timedelta(days=6)
    
    # Get week block
    week_number = report_date.isocalendar()[1]
    week_block = db.session.query(WeekBlock).filter_by(
        user_id=user_id,
        year=report_date.year,
        week_number=week_number
    ).first()
    
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
        'average_rpe': None,
        'weekly_metrics': {
            'rpe': None,
            'gains': None,
            'gratitudes': None
        }
    }
    
    # Initialize days
    current_date = start_date
    while current_date <= report_date:
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
    projects = Project.query.filter_by(user_id=user_id).all()
    for project in projects:
        # Count completed tasks in the date range using Commitment records
        completed_tasks = db.session.query(ProjectTask).join(
            Commitment, Commitment.project_task_id == ProjectTask.id
        ).filter(
            ProjectTask.project_id == project.id,
            Commitment.completed == True,
            Commitment.due_date.between(start_date, report_date)
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
        Routine.user_id == user_id,
        Session.start_time.between(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(report_date, datetime.max.time())
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
        Commitment.user_id == user_id,
        Commitment.completed == True,
        Commitment.project_task_id.isnot(None),
        Commitment.due_date.between(start_date, report_date)
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
        Commitment.user_id == user_id,
        Commitment.completed == True,
        Commitment.due_date.between(start_date, report_date),
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
        Checkin.user_id == user_id,
        Checkin.rpe.isnot(None),
        cast(Checkin.timestamp, Date).between(start_date, report_date)
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
    
    # Add weekly metrics if week block exists
    if week_block:
        report['weekly_metrics'] = {
            'rpe': week_block.rpe,
            'gains': week_block.gains,
            'gratitudes': week_block.gratitudes
        }
    
    return jsonify(report)

@reports_bp.route('/api/reports/day/<date_str>', methods=['GET', 'POST'])
@jwt_required()
def handle_single_day_report(date_str):
    """Handle operations for a single day report"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    try:
        report_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    if request.method == 'GET':
        # Get day block
        day_block = db.session.query(DayBlock).filter_by(
            user_id=user_id,
            year=report_date.year,
            month=report_date.month,
            day=report_date.day
        ).first()

        # Get daily activity data
        sessions = db.session.query(
            Session, Routine
        ).join(
            Routine, Routine.id == Session.routine_id
        ).filter(
            Routine.user_id == user_id,
            func.date(Session.start_time) == report_date,
            Session.completed == True
        ).all()

        # Get completed tasks
        completed_tasks = db.session.query(
            ProjectTask, Commitment
        ).join(
            Commitment, Commitment.project_task_id == ProjectTask.id
        ).filter(
            Commitment.user_id == user_id,
            Commitment.due_date == report_date,
            Commitment.completed == True
        ).all()

        # Get completed catchlist items
        completed_catchlist = db.session.query(
            CatchlistItem, Commitment
        ).join(
            Commitment, Commitment.catchlist_item_id == CatchlistItem.id
        ).filter(
            Commitment.user_id == user_id,
            Commitment.due_date == report_date,
            Commitment.completed == True
        ).all()

        return jsonify({
            'date': report_date.isoformat(),
            'day_block': day_block.as_dict() if day_block else None,
            'sessions': [{
                'id': session.id,
                'title': routine.title,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'rpe': session.rpe,
                'notes': session.notes
            } for session, routine in sessions],
            'completed_tasks': [{
                'id': task.id,
                'title': task.title,
                'completed_at': commitment.completed_at.isoformat() if commitment.completed_at else None
            } for task, commitment in completed_tasks],
            'completed_catchlist': [{
                'id': item.id,
                'content': item.content,
                'completed_at': commitment.completed_at.isoformat() if commitment.completed_at else None
            } for item, commitment in completed_catchlist]
        })
    else:  # POST
        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        # Get or create day block
        day_block = DayBlock.get_or_create(db.session, user_id, report_date.year, report_date.month, report_date.day)

        # Update fields
        if 'sleep_hours' in data:
            day_block.sleep_hours = data['sleep_hours']
        if 'mood' in data:
            day_block.mood = data['mood']
        if 'rpe' in data:
            day_block.rpe = data['rpe']
        if 'food_notes' in data:
            day_block.food_notes = data['food_notes']
        if 'gains' in data:
            day_block.gains = data['gains']
        if 'gratitudes' in data:
            day_block.gratitudes = data['gratitudes']

        db.session.commit()
        return jsonify({"message": "Daily report saved successfully"})

@reports_bp.route('/api/reports/day/range', methods=['GET'])
@jwt_required()
def get_daily_reports_range():
    """Get daily reports for a date range"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401

    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')

    if not start_date_str or not end_date_str:
        return jsonify({"message": "Start date and end date are required"}), 400

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Get all day blocks in the range
    day_blocks = db.session.query(DayBlock).filter(
        DayBlock.user_id == user_id,
        DayBlock.start_date >= start_date,
        DayBlock.start_date <= end_date
    ).order_by(DayBlock.start_date.asc()).all()

    # Get all sessions in the range
    sessions = db.session.query(
        Session, Routine
    ).join(
        Routine, Routine.id == Session.routine_id
    ).filter(
        Routine.user_id == user_id,
        func.date(Session.start_time).between(start_date, end_date),
        Session.completed == True
    ).all()

    # Get all completed tasks in the range
    completed_tasks = db.session.query(
        ProjectTask, Commitment
    ).join(
        Commitment, Commitment.project_task_id == ProjectTask.id
    ).filter(
        Commitment.user_id == user_id,
        Commitment.due_date.between(start_date, end_date),
        Commitment.completed == True
    ).all()

    # Get all completed catchlist items in the range
    completed_catchlist = db.session.query(
        CatchlistItem, Commitment
    ).join(
        Commitment, Commitment.catchlist_item_id == CatchlistItem.id
    ).filter(
        Commitment.user_id == user_id,
        Commitment.due_date.between(start_date, end_date),
        Commitment.completed == True
    ).all()

    # Organize data by date
    reports = {}
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.isoformat()
        reports[date_str] = {
            'date': date_str,
            'day_block': None,
            'sessions': [],
            'completed_tasks': [],
            'completed_catchlist': []
        }
        current_date += timedelta(days=1)

    # Add day blocks
    for block in day_blocks:
        date_str = block.start_date.isoformat()
        if date_str in reports:
            reports[date_str]['day_block'] = block.as_dict()

    # Add sessions
    for session, routine in sessions:
        date_str = session.start_time.date().isoformat()
        if date_str in reports:
            reports[date_str]['sessions'].append({
                'id': session.id,
                'title': routine.title,
                'start_time': session.start_time.strftime('%H:%M'),
                'end_time': session.end_time.strftime('%H:%M'),
                'rpe': session.rpe,
                'notes': session.notes
            })

    # Add completed tasks
    for task, commitment in completed_tasks:
        date_str = commitment.due_date.isoformat()
        if date_str in reports:
            reports[date_str]['completed_tasks'].append({
                'id': task.id,
                'title': task.title,
                'completed_at': commitment.completed_at.isoformat() if commitment.completed_at else None
            })

    # Add completed catchlist items
    for item, commitment in completed_catchlist:
        date_str = commitment.due_date.isoformat()
        if date_str in reports:
            reports[date_str]['completed_catchlist'].append({
                'id': item.id,
                'content': item.content,
                'completed_at': commitment.completed_at.isoformat() if commitment.completed_at else None
            })

    return jsonify(list(reports.values()))

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

@reports_bp.route('/api/reports/daily-summary/<date_str>', methods=['GET', 'POST'])
@jwt_required()
def get_daily_summary(date_str):
    current_user_id = get_current_user_id()
    
    try:
        day_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get or create day block
    day_block = db.session.query(DayBlock).filter_by(
        user_id=current_user_id,
        year=day_date.year,
        month=day_date.month,
        day=day_date.day
    ).first()
    
    if not day_block:
        day_block = DayBlock(
            user_id=current_user_id,
            year=day_date.year,
            month=day_date.month,
            day=day_date.day
        )
        db.session.add(day_block)
        db.session.commit()
    
    if request.method == 'POST':
        data = request.get_json()
        
        # Update day block with new data
        if 'sleep_hours' in data:
            day_block.sleep_hours = float(data['sleep_hours']) if data['sleep_hours'] else None
        if 'mood' in data:
            day_block.mood = int(data['mood']) if data['mood'] else None
        if 'food_notes' in data:
            day_block.food_notes = data['food_notes']
        if 'rpe' in data:
            day_block.rpe = int(data['rpe']) if data['rpe'] else None
        if 'gains' in data:
            day_block.gains = data['gains']
        if 'gratitudes' in data:
            day_block.gratitudes = data['gratitudes']
        
        db.session.commit()
        return jsonify({"message": "Daily report saved successfully"})
    
    # For GET request, return the current data
    return jsonify({
        "sleep_hours": day_block.sleep_hours,
        "mood": day_block.mood,
        "food_notes": day_block.food_notes,
        "rpe": day_block.rpe,
        "gains": day_block.gains,
        "gratitudes": day_block.gratitudes
    })

@reports_bp.route('/api/reports/weekly-report', methods=['POST'])
@jwt_required()
def save_weekly_report():
    """Save weekly report data"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.get_json()
    end_date = data.get('end_date')
    rpe = data.get('rpe')
    gains = data.get('gains')
    gratitudes = data.get('gratitudes')
    
    try:
        report_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get or create week block
    week_number = report_date.isocalendar()[1]
    week_block = WeekBlock.get_or_create(db.session, user_id, report_date.year, week_number)
    
    # Update fields
    if rpe is not None:
        week_block.rpe = rpe
    if gains is not None:
        week_block.gains = gains
    if gratitudes is not None:
        week_block.gratitudes = gratitudes
    
    db.session.commit()
    return jsonify({"message": "Weekly report saved successfully"})

@reports_bp.route('/api/reports/month/range', methods=['GET', 'POST'])
@jwt_required()
def handle_month_range_report():
    """Handle operations for a month range report"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get the year and month from the start date
    year = start_date.year
    month = start_date.month
    
    if request.method == 'GET':
        # Get or create the month block
        month_block = db.session.query(MonthBlock).filter_by(
            user_id=user_id,
            year=year,
            month=month
        ).first()
        
        if not month_block:
            # No month block found, return empty data
            return jsonify({
                'period': {
                    'start_date': start_date_str,
                    'end_date': end_date_str
                },
                'month_theme': None,
                'goals': None,
                'goals_rationale': None,
                'rpe': None,
                'gains': None,
                'gratitudes': None,
                'weekly_metrics': []
            }), 200
        
        # Get weekly blocks for the month
        weekly_blocks = db.session.query(WeekBlock).filter(
            WeekBlock.user_id == user_id,
            WeekBlock.start_date >= start_date,
            WeekBlock.start_date <= end_date
        ).all()
        
        # Format weekly metrics
        weekly_metrics = []
        for block in weekly_blocks:
            weekly_metrics.append({
                'week_number': block.week_number,
                'weekly_aim': block.weekly_aim,
                'weekly_notes': block.weekly_notes,
                'rpe': block.rpe,
                'gains': block.gains,
                'gratitudes': block.gratitudes
            })
        
        # Return month report data
        return jsonify({
            'period': {
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'month_theme': month_block.month_theme,
            'goals': month_block.goals,
            'goals_rationale': month_block.goals_rationale,
            'rpe': month_block.rpe,
            'gains': month_block.gains,
            'gratitudes': month_block.gratitudes,
            'weekly_metrics': weekly_metrics
        })
    
    elif request.method == 'POST':
        # Get data from request
        data = request.get_json()
        
        # Get or create month block
        month_block = db.session.query(MonthBlock).filter_by(
            user_id=user_id,
            year=year,
            month=month
        ).first()
        
        if not month_block:
            # Create a new month block
            month_block = MonthBlock(
                user_id=user_id,
                year=year,
                month=month
            )
            db.session.add(month_block)
        
        # Update month block data
        if 'month_theme' in data:
            month_block.month_theme = data['month_theme']
        if 'goals' in data:
            month_block.goals = data['goals']
        if 'goals_rationale' in data:
            month_block.goals_rationale = data['goals_rationale']
        if 'rpe' in data:
            month_block.rpe = data['rpe']
        if 'gains' in data:
            month_block.gains = data['gains']
        if 'gratitudes' in data:
            month_block.gratitudes = data['gratitudes']
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            'message': 'Monthly report saved successfully',
            'period': {
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'month_theme': month_block.month_theme,
            'goals': month_block.goals,
            'goals_rationale': month_block.goals_rationale,
            'rpe': month_block.rpe,
            'gains': month_block.gains,
            'gratitudes': month_block.gratitudes
        })

@reports_bp.route('/api/reports/season/range', methods=['GET', 'POST'])
@jwt_required()
def handle_season_range_report():
    """Handle operations for a season range report"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get the year and season from the start date
    year = start_date.year
    # Calculate season (1-4) based on month
    month = start_date.month
    season = (month - 1) // 3 + 1
    
    if request.method == 'GET':
        # Get or create the season block
        season_block = db.session.query(SeasonBlock).filter_by(
            user_id=user_id,
            year=year,
            season=season
        ).first()
        
        if not season_block:
            # No season block found, return empty data
            return jsonify({
                'period': {
                    'start_date': start_date_str,
                    'end_date': end_date_str
                },
                'season_theme': None,
                'goals': None,
                'goals_rationale': None,
                'rpe': None,
                'gains': None,
                'gratitudes': None,
                'monthly_metrics': []
            }), 200
        
        # Get monthly blocks for the season
        monthly_blocks = db.session.query(MonthBlock).filter(
            MonthBlock.user_id == user_id,
            MonthBlock.year == year,
            MonthBlock.month >= (season - 1) * 3 + 1,
            MonthBlock.month <= season * 3
        ).all()
        
        # Format monthly metrics
        monthly_metrics = []
        for block in monthly_blocks:
            monthly_metrics.append({
                'month': block.month,
                'month_theme': block.month_theme,
                'goals': block.goals,
                'goals_rationale': block.goals_rationale,
                'rpe': block.rpe,
                'gains': block.gains,
                'gratitudes': block.gratitudes
            })
        
        # Return season report data
        return jsonify({
            'period': {
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'season_theme': season_block.season_theme,
            'goals': season_block.goals,
            'goals_rationale': season_block.goals_rationale,
            'rpe': season_block.rpe,
            'gains': season_block.gains,
            'gratitudes': season_block.gratitudes,
            'monthly_metrics': monthly_metrics
        })
    
    elif request.method == 'POST':
        # Get data from request
        data = request.get_json()
        
        # Get or create season block
        season_block = db.session.query(SeasonBlock).filter_by(
            user_id=user_id,
            year=year,
            season=season
        ).first()
        
        if not season_block:
            # Create a new season block
            season_block = SeasonBlock(
                user_id=user_id,
                year=year,
                season=season
            )
            db.session.add(season_block)
        
        # Update season block data
        if 'season_theme' in data:
            season_block.season_theme = data['season_theme']
        if 'goals' in data:
            season_block.goals = data['goals']
        if 'goals_rationale' in data:
            season_block.goals_rationale = data['goals_rationale']
        if 'rpe' in data:
            season_block.rpe = data['rpe']
        if 'gains' in data:
            season_block.gains = data['gains']
        if 'gratitudes' in data:
            season_block.gratitudes = data['gratitudes']
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            'message': 'Seasonal report saved successfully',
            'period': {
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'season_theme': season_block.season_theme,
            'goals': season_block.goals,
            'goals_rationale': season_block.goals_rationale,
            'rpe': season_block.rpe,
            'gains': season_block.gains,
            'gratitudes': season_block.gratitudes
        })

@reports_bp.route('/api/reports/year/range', methods=['GET', 'POST'])
@jwt_required()
def handle_year_range_report():
    """Handle operations for a year range report"""
    user_id = get_current_user_id()
    if not user_id:
        return jsonify({"message": "Unauthorized"}), 401
    
    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')
    
    if not start_date_str or not end_date_str:
        return jsonify({"message": "Start date and end date are required"}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    
    # Get the year from the start date
    year = start_date.year
    
    if request.method == 'GET':
        # Get or create the year block
        year_block = db.session.query(YearBlock).filter_by(
            user_id=user_id,
            year=year
        ).first()
        
        if not year_block:
            # No year block found, return empty data
            return jsonify({
                'period': {
                    'start_date': start_date_str,
                    'end_date': end_date_str
                },
                'year_theme': None,
                'goals': None,
                'goals_rationale': None,
                'rpe': None,
                'gains': None,
                'gratitudes': None,
                'seasonal_metrics': []
            }), 200
        
        # Get seasonal blocks for the year
        seasonal_blocks = db.session.query(SeasonBlock).filter(
            SeasonBlock.user_id == user_id,
            SeasonBlock.year == year
        ).all()
        
        # Format seasonal metrics
        seasonal_metrics = []
        for block in seasonal_blocks:
            seasonal_metrics.append({
                'season': block.season,
                'season_theme': block.season_theme,
                'goals': block.goals,
                'goals_rationale': block.goals_rationale,
                'rpe': block.rpe,
                'gains': block.gains,
                'gratitudes': block.gratitudes
            })
        
        # Return year report data
        return jsonify({
            'period': {
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'year_theme': year_block.year_theme,
            'goals': year_block.goals,
            'goals_rationale': year_block.goals_rationale,
            'rpe': year_block.rpe,
            'gains': year_block.gains,
            'gratitudes': year_block.gratitudes,
            'seasonal_metrics': seasonal_metrics
        })
    
    elif request.method == 'POST':
        # Get data from request
        data = request.get_json()
        
        # Get or create year block
        year_block = db.session.query(YearBlock).filter_by(
            user_id=user_id,
            year=year
        ).first()
        
        if not year_block:
            # Create a new year block
            year_block = YearBlock(
                user_id=user_id,
                year=year
            )
            db.session.add(year_block)
        
        # Update year block data
        if 'year_theme' in data:
            year_block.year_theme = data['year_theme']
        if 'goals' in data:
            year_block.goals = data['goals']
        if 'goals_rationale' in data:
            year_block.goals_rationale = data['goals_rationale']
        if 'rpe' in data:
            year_block.rpe = data['rpe']
        if 'gains' in data:
            year_block.gains = data['gains']
        if 'gratitudes' in data:
            year_block.gratitudes = data['gratitudes']
        
        # Save to database
        db.session.commit()
        
        return jsonify({
            'message': 'Yearly report saved successfully',
            'period': {
                'start_date': start_date_str,
                'end_date': end_date_str
            },
            'year_theme': year_block.year_theme,
            'goals': year_block.goals,
            'goals_rationale': year_block.goals_rationale,
            'rpe': year_block.rpe,
            'gains': year_block.gains,
            'gratitudes': year_block.gratitudes
        }) 