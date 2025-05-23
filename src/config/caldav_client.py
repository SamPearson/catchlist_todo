import caldav
import icalendar
from datetime import datetime, timedelta
import logging
from dateutil import parser
import pytz
from typing import List, Dict, Optional, Union
from dataclasses import dataclass

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@dataclass
class CalendarInfo:
    name: str
    color: str
    url: str
    uid: str

    def __post_init__(self):
        # Ensure URL is a string
        if hasattr(self.url, 'url'):
            self.url = str(self.url.url)
        else:
            self.url = str(self.url)

@dataclass
class EventInfo:
    summary: str
    description: Optional[str]
    start: datetime
    end: datetime
    rrule: Optional[str]
    uid: str
    recurrence_id: Optional[str]
    timezone: str  # Timezone from VTIMEZONE component

class CalDAVError(Exception):
    """Base exception for CalDAV related errors"""
    pass

class CalDAVConnectionError(CalDAVError):
    """Raised when connection to CalDAV server fails"""
    pass

class CalDAVClient:
    def __init__(self, url: str, username: str, password: str):
        """Initialize CalDAV client with connection details"""
        self.url = url.rstrip('/') + '/'  # Ensure URL ends with slash
        self.username = username
        self.password = password
        self.client = None
        logger.debug(f"Initializing CalDAV client for URL: {self.url}")

    def connect(self) -> bool:
        """Establish connection to CalDAV server"""
        try:
            self.client = caldav.DAVClient(
                url=self.url,
                username=self.username,
                password=self.password
            )
            
            # Test connection by getting principal
            principal = self.client.principal()
            if not principal:
                raise CalDAVConnectionError("Failed to get principal from CalDAV server")
                
            logger.debug("Successfully connected to CalDAV server")
            return True
            
        except caldav.error.AuthorizationError as e:
            raise CalDAVConnectionError(f"Authorization failed: {str(e)}")
        except caldav.error.DAVError as e:
            raise CalDAVConnectionError(f"DAV error: {str(e)}")
        except Exception as e:
            raise CalDAVConnectionError(f"Connection error: {str(e)}")

    def get_calendars(self):
        """Get list of available calendars"""
        try:
            # Get principal URL
            principal = self.client.principal()
            logger.debug(f"Found principal URL: {principal.url}")
            
            # Get calendar home
            calendar_home = principal.calendar_home_set
            logger.debug(f"Found calendar home: {calendar_home.url}")
            
            # Get all calendars
            calendars = calendar_home.calendars()
            logger.debug(f"Found {len(calendars)} calendars")
            
            result = []
            for calendar in calendars:
                try:
                    # Get calendar properties
                    name = calendar.name
                    if not name:
                        name = "Unnamed Calendar"
                    
                    # Get color (default to a neutral gray if not available)
                    color = "#767676"  # Default color
                    
                    # Get UID from URL
                    uid = calendar.url.split('/')[-2] if calendar.url.endswith('/') else calendar.url.split('/')[-1]
                    
                    result.append(CalendarInfo(
                        name=name,
                        color=color,
                        url=calendar.url,
                        uid=uid
                    ))
                    logger.debug(f"Processed calendar: {name} ({uid})")
                except Exception as e:
                    logger.error(f"Error processing calendar {calendar.url}: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting calendars: {str(e)}", exc_info=True)
            raise CalDAVError(f"Failed to get calendars: {str(e)}")

    def get_events(self, calendar_url: str, start_date: Optional[datetime] = None, 
                  end_date: Optional[datetime] = None) -> List[EventInfo]:
        """Get events from a specific calendar"""
        if not self.client:
            raise CalDAVError("Not connected to CalDAV server")
            
        try:
            calendar = self.client.calendar(url=calendar_url)
            
            # Set default date range if not provided
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=365)
                
            logger.debug(f"Searching for events between {start_date} and {end_date}")
            
            # Use search instead of date_search as per deprecation notice
            events = calendar.search(
                start=start_date,
                end=end_date,
                event=True
            )
            logger.debug(f"Found {len(events)} events")
            
            event_list = []
            for event in events:
                try:
                    event_info = self._parse_event(event)
                    if event_info:
                        logger.debug(f"Successfully parsed event: {event_info.summary} (RRULE: {event_info.rrule})")
                        event_list.append(event_info)
                    else:
                        logger.debug("Event parsed but returned None")
                except Exception as e:
                    logger.warning(f"Error parsing event: {str(e)}")
                    continue
            
            return event_list
            
        except Exception as e:
            logger.error(f"Failed to get events: {str(e)}")
            raise CalDAVError(f"Failed to get events: {str(e)}")

    def _parse_event(self, event: caldav.CalendarObjectResource) -> Optional[EventInfo]:
        """Parse a single event into EventInfo object"""
        try:
            # Get raw event data
            raw_data = event.data
            
            # Handle different raw data formats
            if isinstance(raw_data, dict):
                for key in ['data', 'raw', 'ical', 'content']:
                    if key in raw_data:
                        raw_data = raw_data[key]
                        break
                else:
                    raw_data = str(raw_data)
            
            if isinstance(raw_data, dict):
                raw_data = str(raw_data)
            
            # Parse with icalendar
            cal = icalendar.Calendar.from_ical(raw_data)
            
            # Get timezone from VTIMEZONE component
            timezone = 'America/Chicago'  # Default timezone
            for component in cal.walk():
                if component.name == "VTIMEZONE":
                    timezone = str(component.get('TZID', 'America/Chicago'))
                    logger.debug(f"Found timezone in VTIMEZONE component: {timezone}")
                    break
            
            # Find first VEVENT component
            for component in cal.walk():
                if component.name == "VEVENT":
                    # Get basic event details
                    summary = str(component.get('summary', ''))
                    uid = str(component.get('uid'))
                    
                    # Check for recurring event
                    rrule = component.get('rrule')
                    recurrence_id = component.get('recurrence-id')
                    
                    # Log event details for debugging
                    logger.debug(f"Processing event: {summary}")
                    logger.debug(f"RRULE: {rrule}")
                    logger.debug(f"Recurrence ID: {recurrence_id}")
                    
                    # Skip non-recurring events
                    if not rrule and not recurrence_id and 'RRULE' not in raw_data.upper():
                        logger.debug(f"Skipping non-recurring event: {summary}")
                        continue
                    
                    # Get remaining details
                    description = str(component.get('description', ''))
                    
                    # Handle start time with timezone
                    start = component.get('dtstart').dt
                    logger.debug(f"Raw start time: {start}")
                    logger.debug(f"Start time timezone info: {start.tzinfo if isinstance(start, datetime) else 'N/A'}")
                    
                    if isinstance(start, datetime):
                        if start.tzinfo is None:
                            # If no timezone info, use the timezone from VTIMEZONE
                            try:
                                tz = pytz.timezone(timezone)
                                start = tz.localize(start)
                                logger.debug(f"Localized start time: {start}")
                            except pytz.exceptions.UnknownTimeZoneError:
                                logger.warning(f"Unknown timezone {timezone}, using UTC")
                                start = pytz.UTC.localize(start)
                        # Store in original timezone instead of converting to UTC
                        logger.debug(f"Start time in original timezone: {start}")
                    
                    # Handle end time with timezone
                    end = component.get('dtend').dt
                    logger.debug(f"Raw end time: {end}")
                    logger.debug(f"End time timezone info: {end.tzinfo if isinstance(end, datetime) else 'N/A'}")
                    
                    if isinstance(end, datetime):
                        if end.tzinfo is None:
                            # If no timezone info, use the timezone from VTIMEZONE
                            try:
                                tz = pytz.timezone(timezone)
                                end = tz.localize(end)
                                logger.debug(f"Localized end time: {end}")
                            except pytz.exceptions.UnknownTimeZoneError:
                                logger.warning(f"Unknown timezone {timezone}, using UTC")
                                end = pytz.UTC.localize(end)
                        # Store in original timezone instead of converting to UTC
                        logger.debug(f"End time in original timezone: {end}")
                    
                    # Format recurrence_id
                    if recurrence_id:
                        if hasattr(recurrence_id, 'dt'):
                            recurrence_id = recurrence_id.dt
                            if isinstance(recurrence_id, datetime):
                                if recurrence_id.tzinfo is None:
                                    recurrence_id = pytz.UTC.localize(recurrence_id)
                                else:
                                    recurrence_id = recurrence_id.astimezone(pytz.UTC)
                                recurrence_id = recurrence_id.isoformat()
                            else:
                                recurrence_id = str(recurrence_id)
                        else:
                            recurrence_id = str(recurrence_id)
                    
                    # Format rrule to proper iCalendar format
                    if rrule:
                        # Convert vRecur to proper iCalendar format
                        rrule_str = f"FREQ={rrule['FREQ'][0]}"
                        if 'INTERVAL' in rrule:
                            rrule_str += f";INTERVAL={rrule['INTERVAL'][0]}"
                        if 'COUNT' in rrule:
                            rrule_str += f";COUNT={rrule['COUNT'][0]}"
                        if 'UNTIL' in rrule:
                            until = rrule['UNTIL'][0]
                            if isinstance(until, datetime):
                                if until.tzinfo is None:
                                    until = pytz.UTC.localize(until)
                                else:
                                    until = until.astimezone(pytz.UTC)
                                rrule_str += f";UNTIL={until.strftime('%Y%m%dT%H%M%SZ')}"
                            else:
                                rrule_str += f";UNTIL={until}"
                        if 'BYDAY' in rrule:
                            rrule_str += f";BYDAY={','.join(rrule['BYDAY'])}"
                        if 'BYMONTHDAY' in rrule:
                            rrule_str += f";BYMONTHDAY={','.join(map(str, rrule['BYMONTHDAY']))}"
                        if 'BYMONTH' in rrule:
                            rrule_str += f";BYMONTH={','.join(map(str, rrule['BYMONTH']))}"
                        if 'BYSETPOS' in rrule:
                            rrule_str += f";BYSETPOS={','.join(map(str, rrule['BYSETPOS']))}"
                        if 'WKST' in rrule:
                            rrule_str += f";WKST={rrule['WKST'][0]}"
                        logger.debug(f"Formatted RRULE: {rrule_str}")
                        rrule = rrule_str
                    
                    return EventInfo(
                        summary=summary,
                        description=description,
                        start=start,
                        end=end,
                        rrule=rrule,
                        uid=uid,
                        recurrence_id=recurrence_id,
                        timezone=timezone
                    )
            
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing event: {str(e)}")
            return None
