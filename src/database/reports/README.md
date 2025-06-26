
## Models
Five report types, all inheriting base fields:
- DayReport
- WeekReport
- MonthReport
- SeasonReport
- YearReport

Common fields:
- id
- user_id
- created_at
- updated_at
- metadata (JSONB)

## Repository Pattern
- Generic CRUD operations
- Type-safe methods
- Transaction management
- No business logic

## Service Layer
- Business logic
- Data validation
- Date calculations
- Error handling
- Report relationships

## Implementation Rules

### DO
- Use type hints
- Handle errors explicitly
- Follow single responsibility
- Document public interfaces
- Write tests per layer

### DON'T
- Mix business logic in models
- Access DB directly from services
- Skip validation
- Use raw SQL

## Error Handling
- ReportDateError
- ReportExistsError
- ReportValidationError
- ReportStateError

## Testing
- Unit test each layer
- Mock repositories
- Test edge cases
- Validate constraints

## Date Management
- Handle timezones consistently
- Validate date ranges
- Calculate period boundaries
- Season transitions

## Security
- Validate user ownership
- Sanitize inputs
- Type checking
- No cross-user access
