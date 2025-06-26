# API Layer

## Structure
```
api/
├── routes/             # Feature-specific endpoints
├── utils/              # Legacy - do not use.
├── api.py              # Main API setup
└── app_factory.py      # Flask app configuration
```

## Endpoint Design

### Core Principles
- RESTful resource naming
- JWT authentication required
- Consistent error responses
- Input validation

### Response Format
```json
{
  "data": {},           // Response payload
  "error": null,        // Error details if any
  "metadata": {}        // Pagination, timestamps
}
```

### Error Handling
- 400: Bad Request - Invalid input data
- 401: Unauthorized - Missing/invalid token
- 403: Forbidden - Insufficient permissions
- 404: Not Found - Resource doesn't exist
- 500: Server Error - Internal processing error

## Authentication
- JWT required for protected routes
- User context extracted from token
- Role-based access control

## Request Flow
1. Authentication check
2. Input validation
3. Business logic via service layer
4. Response formatting
5. Error handling

## Development Guidelines

### DO
- Use blueprints for feature organization
- Validate all input data
- Handle errors gracefully
- Use service layer for business logic
- Follow REST conventions

### DON'T
- Access database directly from routes
- Mix business logic in endpoints
- Return raw exception details
- Skip input validation
- Expose sensitive information

## Testing Strategy
- Unit test each endpoint
- Test authentication flows
- Validate error responses
- Check input validation

## Security Practices
- Sanitize all inputs
- Validate data types and permissions
- Secure token handling
- Audit authentication attempts
