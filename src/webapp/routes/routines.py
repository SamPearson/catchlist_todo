from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from ...config.models import db, Routine, Session, Calendar, Tag, RoutineTag
from ...config.caldav_client import CalDAVClient
from datetime import datetime, timedelta
from dateutil import rrule
from dateutil.parser import parse
import random

def generate_random_color():
    """Generate a random hex color code"""
    return f"#{random.randint(0, 0xFFFFFF):06x}"

routines_bp = Blueprint('routines', __name__)

@routines_bp.route('/routines')
@jwt_required()
def routines():
    """Display routines page"""
    user_id = get_jwt_identity()
    
    # Get all calendars for the user
    calendars = Calendar.query.filter_by(user_id=user_id).all()
    
    # Get all routines grouped by calendar
    routines_by_calendar = {}
    for calendar in calendars:
        routines = Routine.query.filter_by(
            user_id=user_id,
            calendar_id=calendar.id
        ).all()
        routines_by_calendar[calendar] = routines
    
    return render_template(
        'routines.html',
        calendars=calendars,
        routines_by_calendar=routines_by_calendar
    )

@routines_bp.route('/api/routines/test-connection', methods=['POST'])
@jwt_required()
def test_caldav_connection():
    """Test CalDAV connection and return available calendars"""
    data = request.get_json()
    
    if not data or not data.get('url') or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        client = CalDAVClient(
            url=data['url'],
            username=data['username'],
            password=data['password']
        )
        
        calendars = client.get_calendars()
        return jsonify({
            "success": True,
            "calendars": calendars
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@routines_bp.route('/api/routines/import', methods=['POST'])
@jwt_required()
def import_routines():
    """Import routines from selected calendars"""
    data = request.get_json()
    
    if not data or not data.get('url') or not data.get('username') or not data.get('password'):
        return jsonify({"message": "Missing required fields"}), 400
    
    try:
        client = CalDAVClient(
            url=data['url'],
            username=data['username'],
            password=data['password']
        )
        
        calendars = client.get_calendars()
        selected_indices = data.get('calendar_indices', [])
        selected_calendars = [calendars[i] for i in selected_indices if i < len(calendars)]
        
        imported_count = 0
        for calendar in selected_calendars:
            events = client.get_events(calendar['url'])
            for event in events:
                if not event.get('rrule'):
                    continue
                
                # Create calendar object if it doesn't exist
                calendar_obj = Calendar.query.filter_by(
                    user_id=get_jwt_identity(),
                    external_uid=calendar['uid']
                ).first()
                
                if not calendar_obj:
                    calendar_obj = Calendar(
                        name=calendar['name'],
                        color=calendar.get('color', '#767676'),
                        user_id=get_jwt_identity(),
                        external_uid=calendar['uid'],
                        external_source='caldav'
                    )
                    db.session.add(calendar_obj)
                    db.session.flush()
                
                # Get timezone from event or use UTC as fallback
                timezone = event.get('timezone', 'UTC')
                
                # Create routine
                routine = Routine(
                    title=event['summary'],
                    description=event.get('description'),
                    rrule=event['rrule'],
                    active=True,
                    user_id=get_jwt_identity(),
                    calendar_id=calendar_obj.id,
                    external_uid=event['uid'],
                    external_source='caldav',
                    external_source_name=calendar['name'],
                    timezone=timezone
                )
                db.session.add(routine)
                db.session.flush()
                
                # Create initial session from the event
                session = Session(
                    routine_id=routine.id,
                    start_time=event['start'],
                    end_time=event['end'],
                    user_id=get_jwt_identity(),
                    timezone=timezone
                )
                db.session.add(session)
                db.session.flush()
                
                # Create or get calendar tag
                calendar_tag = Tag.query.filter_by(
                    user_id=get_jwt_identity(),
                    name=calendar['name']
                ).first()
                
                if not calendar_tag:
                    calendar_tag = Tag(
                        name=calendar['name'],
                        color=generate_random_color(),
                        user_id=get_jwt_identity()
                    )
                    db.session.add(calendar_tag)
                    db.session.flush()
                
                # Associate routine with calendar tag
                routine_tag = RoutineTag(
                    routine_id=routine.id,
                    tag_id=calendar_tag.id
                )
                db.session.add(routine_tag)
                
                imported_count += 1
        
        db.session.commit()
        return jsonify({
            "success": True,
            "imported_count": imported_count
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500

@routines_bp.route('/routines/<int:routine_id>')
@jwt_required()
def show(routine_id):
    return render_template('routines/show.html', routine_id=routine_id) 