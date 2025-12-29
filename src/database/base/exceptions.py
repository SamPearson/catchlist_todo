
class DatabaseError(Exception):
    """Base exception for all database-related errors."""
    pass

class RepositoryError(DatabaseError):
    """Exception raised for errors in repository operations."""
    pass

class ValidationError(DatabaseError):
    """Exception raised for data validation errors."""
    pass

class UserOwnershipError(DatabaseError):
    """Exception raised for user ownership validation failures."""
    pass

class EntityNotFoundError(DatabaseError):
    """Exception raised when an entity cannot be found."""
    pass

class InvalidStateError(DatabaseError):
    """Exception raised when an operation is invalid for the current state."""
    pass

class RelationshipError(DatabaseError):
    """Exception raised for errors in entity relationships."""
    pass