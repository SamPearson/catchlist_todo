# Personal Development Task Manager
## System Requirements Document

### 1. Project Vision
Functionally, what we're doing here is simple.
It's a todo app.

In another sense, it's a resume project. 
This project will demonstrate the ability to:
- establish data models
- build an API
- build an api testing framework
- build a webapp that accesses the API
- build a frontend testing framework
- build and maintain a ci/cd system with integrated testing

Because it is both of these things, it'll be a self-improvement system that pulls me towards it with professional development instead of annoying notifications and dark patterns.

### 2.1 Primary Data Entities

1. **Tasks**
    - Standalone entities. 
    - The entries on a todo list. 
    - Eg "buy a hat"
2. **Projects**
   - Larger goals that consist of many tasks.
   - contains subtasks
   - Eg "learn guitar" 
3. **Events**
   - A 
3. **Routines**
   - asdf
4. **Tags**
user-scoped and user-defined categories that can be applied to other entities

#### 2.2 Supporting Entities

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


### 3. Core Features

Tasks, Projects, and Tags will each have pages where the user can perform search and CRUD operations.

There will be a "desk" page that shows 
