# Personal Development Task Manager
## System Requirements Document

### 1. Project Vision
The system serves as a personal development tracking tool that bridges the gap between intention and action. It's designed to make personal growth measurable and actionable through careful task and commitment tracking.

### 2. Core Philosophy
- **Single User Focus**: Designed specifically for personal use, allowing for precise optimization without compromise
- **Self-Reinforcing**: Acts as both a portfolio project and personal tool, creating a positive feedback loop for engagement
- **Intentional Design**: Focuses on making task engagement deliberate and meaningful

### 3. Data Entities

#### 3.1 Primary Entities
1. **Catchlist Items**
   - Standalone, atomic tasks
   - Properties: content, status, creation date
   - Example: "Buy new hat"

2. **Projects**
   - Large-scale goals requiring multiple steps
   - Contains multiple subtasks
   - Example: "Learn guitar"

3. **Project Subtasks**
   - Components of larger projects
   - Linked to parent project
   - Similar to catchlist items but with project context

4. **Routines**
   - Template for recurring time-boxed activities
   - Properties: title, schedule (RRULE), duration
   - Can be imported from ICS files
   - Generates Sessions based on schedule
   - Example: "Leg Day every Monday"

5. **Sessions**
   - Concrete instances of Routines
   - Properties: start_time, end_time, routine_id
   - Automatically generates associated Commitments
   - Example: "Leg Day on Monday, June 8th, 2025"

6. **Principles**
   - Abstract qualities or values
   - Trackable through adherence
   - Example: "Be more reliable"

#### 3.2 Supporting Entities

1. **Timeframes**
   - Hierarchical time periods
   - Levels: Day, Week, Month, Season, Year
   - Primary organizer for Reports
   - Contains specific start/end dates

2. **Reports**
   - Direct association with Timeframes (1:1)
   - Types: Daily, Weekly, Monthly, Seasonal, Annual
   - Contains:
     - Associated Timeframe
     - List of Commitments within timeframe
     - Metadata fields (sleep, mood, food, gratitude)
     - Notes field
     - Other timeframe-specific metrics

3. **Commitments**
   - Links tasks/sessions to timeframes
   - Properties: due_date, status
   - Can be associated with:
     - Catchlist Items
     - Project Subtasks
     - Sessions
   - Appears in Reports via Timeframe association

4. **Checkins**
   - Timestamp-based progress tracking
   - Optional comments
   - Applicable to all primary entities

### 4. Core Features

#### 4.1 Entity Management
- CRUD operations for all primary entities
- Dedicated management pages for each entity type
- Ability to link entities (e.g., tasks to projects)

#### 4.2 Desk Interface
- Timeline-based view of commitments
- Report generation by timeframe
- Task completion tracking
- Check-in logging
- Notes and metadata capture

#### 4.3 Planning Features
- Forward-looking commitment scheduling
- Historical record viewing
- Progress tracking across timeframes

#### 4.4 Routine & Session Management
- ICS file import capability
- Automatic Session generation from Routine schedules
- Bulk Session creation for specified timeframes
- Automatic Commitment creation for Sessions
- Calendar integration and sync

### 5. Nice-to-Have Features
- Tagging system
- Statistical analysis
  - Completion rates by tag
  - Trend analysis
  - Progress metrics

### 6. Technical Considerations
- Common data structure for task-like entities
- Unified handling of commitments
- Consistent check-in mechanism across entity types
- Efficient querying for report generation

### 7. Migration Notes
Current implementation includes:
- Working API and webapp
- CI/CD pipeline with Jenkins
- Selenium and Postman tests
- Need for architectural consolidation of common patterns

### 8. Next Steps
1. Identify common patterns in existing implementation
2. Design unified data structures
3. Plan incremental migration strategy
4. Develop comprehensive test suite
5. Implement architectural improvements
