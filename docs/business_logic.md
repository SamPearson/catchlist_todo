# Business Logic Documentation

## Core Entities

### 1. Task-Like Entities

#### Tasks
- Represent simple, atomic tasks or thoughts
- Should be completable within a day
- Properties:
  - Content
  - Status (active/completed)
  - Creation date
- Can be converted to:
  - Projects
  - Project subtasks

#### Projects
- Represent longer-term, well-defined goals
- Required components (GTD methodology):
  - Next action
  - Purpose ("why")
- Contains multiple subtasks
- Properties:
  - Title
  - Description
  - Win condition
  - Reason/Purpose
  - Next step
  - Status

### 2. Time-Based Entities

#### Routines
- Represent recurring behavior patterns
- Properties:
  - Title
  - Schedule (RRULE format)
  - Status (active/inactive)
  - Description
- Generates Sessions automatically

#### Sessions
- Concrete instances of Routines
- Properties:
  - Start time
  - End time
  - Completion status
  - Parent Routine reference

### 3. Time Organization

#### Timeframes
Hierarchical structure of time periods:
1. Day
2. Week
3. Month
4. Season
5. Year

Each timeframe:
- Has defined start/end dates
- Contains associated commitments
- Generates corresponding reports

#### Commitments
Two types:
1. **Hard Commitments**
   - Specific date/time
   - Can be associated with:
     - Catchlist items
     - Project subtasks
     - Sessions

2. **Soft Commitments**
   - Flexible timeframe (e.g., "by end of month")
   - Can be associated with:
     - Projects
     - Routines
   - Must specify timeframe (week/month/season/year)

### 4. Progress Tracking

#### Checkins
- Universal progress tracking mechanism
- Components:
  - Timestamp
  - Notes/Comments
  - Optional metrics
- Can be attached to:
  - Catchlist items
  - Projects
  - Routines
  - Sessions
  - Timeframes

#### Reports
- Generated for each timeframe
- Contains:
  - All commitments within timeframe
  - Completed items
  - Progress metrics
  - Notes and metadata
- Features:
  - PDF export capability
  - Historical data analysis
  - Progress visualization

### 5. Categorization Systems

#### Tags
- Properties:
  - Name
  - Color
- Can be attached to:
  - Catchlist items
  - Projects
  - Routines
  - Sessions
  - Reports

#### Principles
- Represent core values or "why" statements
- Can be associated with any entity
- Used for:
  - Motivation tracking
  - Goal alignment
  - Progress evaluation

## Business Rules

1. **Task Management**
   - Catchlist items must be atomic and completable
   - Projects must have a defined next action and purpose
   - Tasks can be converted between types as needed

2. **Time Management**
   - Sessions are automatically generated from Routine schedules
   - Hard commitments require specific dates
   - Soft commitments must specify a timeframe

3. **Progress Tracking**
   - All primary entities can receive checkins
   - Reports are generated automatically for timeframes
   - Historical data must be preserved

4. **Categorization**
   - Entities can have multiple tags
   - Principles can be attached to provide context
   - Tags and principles must be user-defined

## Implementation Notes

1. **Data Integrity**
   - Maintain relationships between related entities
   - Preserve historical data
   - Handle cascading updates/deletes appropriately

2. **User Experience**
   - Provide clear conversion paths between entity types
   - Enable flexible categorization
   - Support both immediate and long-term planning

3. **Reporting**
   - Generate printable/exportable reports
   - Maintain historical records
   - Enable progress analysis