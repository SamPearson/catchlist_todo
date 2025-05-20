import caldav
import icalendar
from datetime import datetime, timedelta
import logging


class CalDAVClient:
    def __init__(self, url, username=None, password=None):
        self.url = url
        self.username = username
        self.password = password
        self.client = None
        
    def connect(self):
        """Establish connection to CalDAV server"""
        try:
            # Ensure URL ends with a slash
            if not self.url.endswith('/'):
                self.url += '/'
                
            # Create client with basic authentication
            self.client = caldav.DAVClient(
                url=self.url,
                username=self.username,
                password=self.password
            )
            
            # Test the connection by getting the principal
            principal = self.client.principal()
            if not principal:
                logging.error("Failed to get principal from CalDAV server")
                return False
                
            return True
        except caldav.error.AuthorizationError as e:
            logging.error(f"CalDAV authorization error: {str(e)}")
            return False
        except caldav.error.DAVError as e:
            logging.error(f"CalDAV DAV error: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"CalDAV connection error: {str(e)}")
            return False
            
    def get_calendars(self):
        """Get list of available calendars"""
        if not self.client:
            if not self.connect():
                return []
                
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
            
            # Log calendar details for debugging
            for cal in calendars:
                logging.info(f"Found calendar: {cal.name} at {cal.url}")
                
            return calendars
        except caldav.error.AuthorizationError as e:
            logging.error(f"CalDAV authorization error while fetching calendars: {str(e)}")
            return []
        except Exception as e:
            logging.error(f"Error fetching calendars: {str(e)}")
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
        """
        Get events from calendar and convert to dictionary format
        
        Args:
            calendar: Calendar object to fetch events from
            start_date: Start date for date range search (datetime object)
            end_date: End date for date range search (datetime object)
            
        Returns:
            List of event dictionaries
        """
        events = self.get_events(calendar, start_date, end_date)
        result = []
        
        for event in events:
            try:
                event_data = event.data
                ical = icalendar.Calendar.from_ical(event_data)
                
                for component in ical.walk():
                    if component.name == "VEVENT":
                        dtstart = component.get('dtstart')
                        dtend = component.get('dtend')
                        
                        # Skip if no start/end
                        if not dtstart or not dtend:
                            continue
                            
                        start_dt = dtstart.dt
                        end_dt = dtend.dt
                        
                        # Convert to datetime if date
                        if not isinstance(start_dt, datetime):
                            start_dt = datetime.combine(start_dt, datetime.min.time())
                        if not isinstance(end_dt, datetime):
                            end_dt = datetime.combine(end_dt, datetime.min.time())
                        
                        # If there's a recurring rule, expand it
                        rrule = component.get('rrule')
                        if rrule:
                            # Use the base event
                            result.append({
                                'uid': str(component.get('uid')),
                                'summary': str(component.get('summary', '')),
                                'description': str(component.get('description', '')),
                                'location': str(component.get('location', '')),
                                'start': start_dt,
                                'end': end_dt,
                                'rrule': str(rrule)
                            })
                            
                            # TODO: Expand recurring events based on the rrule
                            # This is a simplistic approach - for a complete solution
                            # we would need to use dateutil.rrule to expand all instances
                        else:
                            # Non-recurring event
                            result.append({
                                'uid': str(component.get('uid')),
                                'summary': str(component.get('summary', '')),
                                'description': str(component.get('description', '')),
                                'location': str(component.get('location', '')),
                                'start': start_dt,
                                'end': end_dt
                            })
            except Exception as e:
                print(f"Error parsing event: {str(e)}")
                continue
                
        return result
