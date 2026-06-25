"""
Presenter for routines - handles timezone conversion for API responses.
Converts routine times from stored timezone to user's display timezone.
"""

from typing import Dict, Any
from src.utils.timezone import convert_time_between_timezones


class RoutinePresenter:
    """Presents routines with times converted to user's timezone for display."""

    @staticmethod
    def present_for_user(routine, user_timezone: str) -> Dict[str, Any]:
        """
        Convert a routine for API response, adjusting times if necessary.

        Args:
            routine: Routine model instance
            user_timezone: User's IANA timezone string for display (e.g., 'America/Chicago')

        Returns:
            Dictionary representation of routine with times in user's timezone
        """
        routine_dict = routine.as_dict()
        stored_timezone = routine_dict.get('timezone', 'UTC')
        
        if stored_timezone != user_timezone and routine_dict.get('start_time') and routine_dict.get('end_time'):
            # Use your existing timezone utility functions
            routine_dict['start_time'] = convert_time_between_timezones(
                routine_dict['start_time'], stored_timezone, user_timezone
            )
            routine_dict['end_time'] = convert_time_between_timezones(
                routine_dict['end_time'], stored_timezone, user_timezone
            )
        
        return routine_dict

    @staticmethod
    def present_list_for_user(routines, user_timezone: str):
        """
        Convert a list of routines for API response.

        Args:
            routines: List of routine model instances
            user_timezone: User's IANA timezone string for display

        Returns:
            List of dictionaries with times in user's timezone
        """
        return [RoutinePresenter.present_for_user(r, user_timezone) for r in routines]