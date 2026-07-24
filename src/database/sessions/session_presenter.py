"""
Presenter for sessions - handles timezone conversion for API responses.
Converts session times from stored timezone to user's display timezone.
"""

from typing import Dict, List, Any
from datetime import datetime
from zoneinfo import ZoneInfo


class SessionPresenter:
    """Presents sessions with times converted to user's timezone for display."""

    @staticmethod
    def present_for_user(session, user_timezone: str) -> Dict[str, Any]:
        """
        Convert a session for API response, adjusting datetimes if necessary.

        Sessions are stored with naive datetimes in their stored timezone.
        This converts them to the user's display timezone if different.

        Args:
            session: RoutineSession model instance
            user_timezone: User's IANA timezone string for display (e.g., 'America/Chicago')

        Returns:
            Dictionary representation of session with times in user's timezone
        """
        session_dict = session.as_dict()

        stored_timezone = session_dict.get('timezone', 'UTC')

        # If timezones match, no conversion needed
        if stored_timezone == user_timezone:
            return session_dict

        # Convert times from stored timezone to user's timezone
        if session_dict.get('start_time') and session_dict.get('end_time'):
            try:
                # Parse the ISO datetime strings (naive)
                start_dt_str = session_dict['start_time']
                end_dt_str = session_dict['end_time']

                # Convert strings to datetime objects
                start_dt_naive = datetime.fromisoformat(start_dt_str.replace('Z', '+00:00'))
                end_dt_naive = datetime.fromisoformat(end_dt_str.replace('Z', '+00:00'))

                # Localize to stored timezone
                stored_tz = ZoneInfo(stored_timezone)
                start_dt_stored = start_dt_naive.replace(tzinfo=stored_tz)
                end_dt_stored = end_dt_naive.replace(tzinfo=stored_tz)

                # Convert to user's timezone
                user_tz = ZoneInfo(user_timezone)
                start_dt_user = start_dt_stored.astimezone(user_tz)
                end_dt_user = end_dt_stored.astimezone(user_tz)

                # Remove timezone info and return ISO format (for datetime-local input)
                session_dict['start_time'] = start_dt_user.replace(tzinfo=None).isoformat()
                session_dict['end_time'] = end_dt_user.replace(tzinfo=None).isoformat()

            except Exception as e:
                # If conversion fails, return as-is
                import logging
                logging.error(f"Error converting session times: {e}")

        return session_dict

    @staticmethod
    def present_list_for_user(sessions, user_timezone: str) -> List[Dict[str, Any]]:
        """
        Convert a list of sessions for API response.

        Args:
            sessions: List of RoutineSession model instances
            user_timezone: User's IANA timezone string for display

        Returns:
            List of dictionaries with times in user's timezone
        """
        return [SessionPresenter.present_for_user(s, user_timezone) for s in sessions]