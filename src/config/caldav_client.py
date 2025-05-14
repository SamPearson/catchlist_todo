import caldav
import icalendar
from datetime import datetime, timedelta


class CalDAVClient:
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.client = None
        
    def connect(self):
        """Establish connection to CalDAV server"""
        try:
            self.client = caldav.DAVClient(
                url=self.url,
                username=self.username,
                password=self.password
            )
            return True
        except Exception as e:
            print(f"CalDAV connection error: {str(e)}")
            return False
            
    def get_calendars(self):
        """Get list of available calendars"""
        if not self.client:
            if not self.connect():
                return []
                
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
            return calendars
        except Exception as e:
            print(f"Error fetching calendars: {str(e)}")
            return []
            
    def get_events(self, calendar=None, start_date=None, end_date=None):
        """Get events from a specific calendar within date range"""
        if not calendar:
            calendars = self.get_calendars()
            if not calendars:
                return []
            calendar = calendars[0]  # Use first calendar by default
            
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now() + timedelta(days=90)
            
        try:
            events = calendar.date_search(start=start_date, end=end_date)
            return events
        except Exception as e:
            print(f"Error fetching events: {str(e)}")
            return []
            
    def get_events_as_dict(self, calendar=None, start_date=None, end_date=None):
        """Get events formatted as a dictionary"""
        events = self.get_events(calendar, start_date, end_date)
        result = []
        
        for event in events:
            try:
                ical_data = event.data
                cal = icalendar.Calendar.from_ical(ical_data)
                
                for component in cal.walk('VEVENT'):
                    event_dict = {
                        'uid': str(component.get('UID', '')),
                        'summary': str(component.get('SUMMARY', '')),
                        'description': str(component.get('DESCRIPTION', '')),
                        'start': component.get('DTSTART').dt if component.get('DTSTART') else None,
                        'end': component.get('DTEND').dt if component.get('DTEND') else None,
                        'rrule': str(component.get('RRULE', ''))
                    }
                    result.append(event_dict)
            except Exception as e:
                print(f"Error parsing event: {str(e)}")
                
        return result
    