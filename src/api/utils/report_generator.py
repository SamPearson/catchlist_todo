from datetime import datetime, timedelta
from ...config.models import db, Report, Checkin

class ReportGenerator:
    @staticmethod
    def generate_missing_reports(user_id, session):
        """Generate any missing reports for the user"""
        # Get the latest report date
        latest_report = Report.query.filter_by(user_id=user_id).order_by(Report.date.desc()).first()
        
        # If no reports exist, start from 30 days ago
        start_date = latest_report.date if latest_report else datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
        
        # Generate reports for each day in the range
        current_date = start_date
        while current_date <= end_date:
            # Skip if report already exists
            existing_report = Report.query.filter_by(
                user_id=user_id,
                date=current_date
            ).first()
            
            if not existing_report:
                # Get checkins for the day
                checkins = Checkin.query.filter(
                    Checkin.user_id == user_id,
                    db.func.date(Checkin.timestamp) == current_date
                ).all()
                
                # Calculate daily metrics
                total_rpe = sum(c.rpe or 0 for c in checkins)
                total_mood = sum(c.mood or 0 for c in checkins)
                total_energy = sum(c.energy or 0 for c in checkins)
                checkin_count = len(checkins)
                
                # Create new report
                report = Report(
                    user_id=user_id,
                    date=current_date,
                    rpe=total_rpe / checkin_count if checkin_count > 0 else None,
                    mood=total_mood / checkin_count if checkin_count > 0 else None,
                    energy=total_energy / checkin_count if checkin_count > 0 else None,
                    checkin_count=checkin_count
                )
                session.add(report)
            
            current_date += timedelta(days=1)
        
        session.commit() 