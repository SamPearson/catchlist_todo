from typing import Optional, Dict
import pytz
from .repository import UserRepository
from .models import User
from src.database.base.exceptions import ValidationError


class UserValidationError(ValidationError):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


def validate_timezone(timezone: str) -> str:
    """
    Validate that the timezone string is a valid IANA timezone.
    Returns the validated timezone string.
    Raises UserValidationError if invalid.
    """
    if not timezone:
        return "UTC"
    
    timezone = timezone.strip()
    
    if len(timezone) > 64:
        raise UserValidationError("Timezone string too long")
    
    # Check if it's a valid IANA timezone
    try:
        pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise UserValidationError(f"Invalid timezone: {timezone}. Must be a valid IANA timezone (e.g., 'America/Chicago', 'UTC', 'Europe/London')")
    
    return timezone


class UserService:
    """Service layer for user operations"""

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user_timezone(self, user_id: int) -> str:
        """
        Get the timezone for a user by ID.
        Returns 'UTC' if user not found or has no timezone set.

        This is a convenience method for getting user timezone in API handlers.

        Args:
            user_id: The user's ID

        Returns:
            The user's timezone string (IANA format)
        """
        user = self.repository.get(user_id)
        return user.timezone if user and user.timezone else 'UTC'

    def register_user(self, username: str, password: str,
                     name: Optional[str] = None, timezone: str = "UTC") -> User:
        """Register a new user"""
        # Validate username
        username = (username or "").strip()
        if not username:
            raise UserValidationError("Username is required")
        
        if len(username) < 3:
            raise UserValidationError("Username must be at least 3 characters")
        
        if len(username) > 80:
            raise UserValidationError("Username cannot exceed 80 characters")
        
        if self.repository.username_exists(username):
            raise UserValidationError("Username already exists")
        
        # Validate password
        if not password:
            raise UserValidationError("Password is required")
        
        if len(password) < 6:
            raise UserValidationError("Password must be at least 6 characters")
        
        # Validate timezone
        timezone = validate_timezone(timezone)
        
        # Create the user
        return self.repository.create_user(
            username=username,
            password=password,
            name=name,
            timezone=timezone
        )

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        if not username or not password:
            return None
        
        user = self.repository.get_by_username(username)
        if user and user.check_password(password):
            return user
        
        return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return self.repository.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.repository.get_by_username(username)

    def update_user(self, user: User, data: Dict) -> User:
        """Update user information"""
        update_data = {}
        
        if 'name' in data:
            name = (data['name'] or "").strip() if data['name'] else None
            if name and len(name) > 64:
                raise UserValidationError("Name cannot exceed 64 characters")
            update_data['name'] = name
        
        if 'timezone' in data:
            timezone = validate_timezone(data['timezone'])
            update_data['timezone'] = timezone
        
        if update_data:
            return self.repository.update(user, **update_data)
        
        return user

    def change_password(self, user: User, old_password: str, new_password: str) -> User:
        """Change a user's password"""
        if not user.check_password(old_password):
            raise UserValidationError("Current password is incorrect")
        
        if not new_password:
            raise UserValidationError("New password is required")
        
        if len(new_password) < 6:
            raise UserValidationError("New password must be at least 6 characters")
        
        return self.repository.update_password(user, new_password)

    def delete_user(self, user: User) -> None:
        """Delete a user account"""
        # All cascade deletes are handled by the User model relationships
        self.repository.delete(user)