# Frontend Integration Guide

## Overview

This document outlines how the database models are exposed through the API and integrated with frontend components. Understanding these data flows is critical for maintaining consistency between the backend and frontend.

## Data Flow Architecture

```
Database Models → API Controllers → JSON Response → Frontend Components
```

## UI Component Requirements

### Desk Page

The Desk page is the centerpiece of the application and requires data from multiple models:

#### Main Timeline View

**Required Data:**
```json
{
  "commitments": [
    {
      "id": 1,
      "entity_type": "catchlist_item",
      "entity_id": 42,
      "entity": {
        "id": 42,
        "content": "Buy groceries",
        "status": "active",
        "tags": [{"id": 1, "name": "errands", "color": "#FF5733"}]
      },
      "due_date": "2025-06-05",
      "time_box": "01:30:00",
      "completed": false
    },
    {
      "id": 2,
      "entity_type": "project_task",
      "entity_id": 15,
      "entity": {
        "id": 15,
        "content": "Draft chapter 3",
        "status": "pending",
        "project": {
          "id": 5,
          "title": "Write novel"
        }
      },
      "due_date": "2025-06-05",
      "time_box": null,
      "completed": false
    },
    {
      "id": 3,
      "entity_type": "session",
      "entity_id": 28,
      "entity": {
        "id": 28,
        "routine": {
          "id": 7,
          "title": "Morning yoga"
        },
        "start_time": "2025-06-05T08:00:00",
        "end_time": "2025-06-05T09:00:00",
        "status": "scheduled"
      },
      "due_date": "2025-06-05",
      "time_box": "01:00:00",
      "completed": false
    }
  ],
  "current_timeframe": {
    "id": 123,
    "type": "day",
    "start_date": "2025-06-05",
    "end_date": "2025-06-05",
    "report": {
      "id": 456,
      "metadata": {
        "sleep": 7.5,
        "mood": "good",
        "notes": "Productive day!"
      }
    }
  }
}
```

**API Endpoints:**
- `GET /api/commitments?start_date=X&end_date=Y`
- `GET /api/timeframes/current?type=day`
- `GET /api/reports?timeframe_id=123`

**Component Structure:**
- DeskPage (container)
  - TimeframeSelector
  - TimelineView
    - CommitmentCard (multiple)
  - DailyReportPanel
    - MetadataForm
    - NotesEditor

### Project Management Page

**Required Data:**
```json
{
  "projects": [
    {
      "id": 5,
      "title": "Write novel",
      "description": "Complete first draft of sci-fi novel",
      "status": "active",
      "due_date": "2025-08-15",
      "principle": {
        "id": 3,
        "title": "Creative expression"
      },
      "tasks": [
        {
          "id": 15,
          "content": "Draft chapter 3",
          "status": "pending",
          "order": 3,
          "due_date": "2025-06-05",
          "commitments": [
            {
              "id": 2,
              "due_date": "2025-06-05",
              "completed": false
            }
          ]
        }
      ],
      "tags": [
        {"id": 2, "name": "writing", "color": "#3498DB"}
      ],
      "check_ins": [
        {
          "id": 7,
          "timestamp": "2025-06-01T14:30:00",
          "note": "Making good progress"
        }
      ]
    }
  ],
  "principles": [
    {"id": 3, "title": "Creative expression"},
    {"id": 4, "title": "Learning"},
    {"id": 5, "title": "Health"}
  ],
  "tags": [
    {"id": 2, "name": "writing", "color": "#3498DB"},
    {"id": 3, "name": "creative", "color": "#9B59B6"},
    {"id": 4, "name": "long-term", "color": "#2ECC71"}
  ]
}
```

**API Endpoints:**
- `GET /api/projects`
- `GET /api/projects/{id}`
- `GET /api/principles`
- `GET /api/tags`

**Component Structure:**
- ProjectListPage
  - ProjectCard (multiple)
  - NewProjectForm
- ProjectDetailPage
  - ProjectHeader
  - TaskList
    - TaskItem (multiple)
  - CheckinPanel
  - TagSelector

### Routine Management Page

**Required Data:**
```json
{
  "routines": [
    {
      "id": 7,
      "title": "Morning yoga",
      "description": "30 minutes of yoga practice",
      "schedule": "FREQ=DAILY;BYDAY=MO,WE,FR",
      "duration": "00:30:00",
      "status": "active",
      "tags": [
        {"id": 5, "name": "exercise", "color": "#E74C3C"}
      ],
      "upcoming_sessions": [
        {
          "id": 28,
          "start_time": "2025-06-05T08:00:00",
          "end_time": "2025-06-05T08:30:00",
          "status": "scheduled"
        },
        {
          "id": 29,
          "start_time": "2025-06-07T08:00:00",
          "end_time": "2025-06-07T08:30:00",
          "status": "scheduled"
        }
      ]
    }
  ],
  "tags": [
    {"id": 5, "name": "exercise", "color": "#E74C3C"},
    {"id": 6, "name": "morning", "color": "#F39C12"},
    {"id": 7, "name": "health", "color": "#16A085"}
  ]
}
```

**API Endpoints:**
- `GET /api/routines`
- `GET /api/routines/{id}`
- `GET /api/routines/{id}/sessions?start_date=X&end_date=Y`
- `GET /api/tags`

**Component Structure:**
- RoutineListPage
  - RoutineCard (multiple)
  - NewRoutineForm
- RoutineDetailPage
  - RoutineHeader
  - ScheduleEditor
  - SessionList
    - SessionItem (multiple)
  - TagSelector

## Commitment Management

Commitments are a central concept that connect various entities to timeframes:

### Creating Commitments

**Request Format:**
```json
{
  "entity_type": "project_task",
  "entity_id": 15,
  "due_date": "2025-06-05",
  "time_box": "01:30:00" // optional
}
```

**API Endpoint:**
- `POST /api/commitments`

### Updating Commitments

**Request Format:**
```json
{
  "due_date": "2025-06-06", // optional, for rescheduling
  "time_box": "02:00:00",  // optional
  "completed": true        // optional, for marking complete
}
```

**API Endpoint:**
- `PATCH /api/commitments/{id}`

### Commitment Timeline View

The timeline view requires efficient querying of commitments across a date range:

**API Endpoint:**
- `GET /api/commitments?start_date=2025-06-01&end_date=2025-06-07`

**Response Format:**
```json
{
  "commitments": [
    {
      "id": 1,
      "entity_type": "catchlist_item",
      "entity": { /* entity data */ },
      "due_date": "2025-06-01",
      "completed": true
    },
    // ... more commitments grouped by date
  ],
  "timeframes": [
    {
      "type": "day",
      "start_date": "2025-06-01",
      "end_date": "2025-06-01",
      "report": { /* report data if exists */ }
    },
    // ... more timeframes in the range
  ]
}
```

## Reporting System

### Daily Report

**Required Data:**
```json
{
  "timeframe": {
    "id": 123,
    "type": "day",
    "start_date": "2025-06-05",
    "end_date": "2025-06-05"
  },
  "report": {
    "id": 456,
    "metadata": {
      "sleep": 7.5,
      "mood": "good",
      "energy": 8,
      "gratitude": "Family support"
    },
    "notes": "Productive day focused on the novel project."
  },
  "commitments": [
    {
      "id": 1,
      "entity_type": "catchlist_item",
      "entity": { /* entity data */ },
      "completed": true,
      "completed_at": "2025-06-05T15:30:00"
    },
    // ... more commitments
  ],
  "stats": {
    "total": 5,
    "completed": 3,
    "completion_rate": 0.6
  }
}
```

**API Endpoints:**
- `GET /api/timeframes?type=day&date=2025-06-05`
- `GET /api/reports?timeframe_id=123`
- `GET /api/commitments?timeframe_id=123`

### Weekly Report

**Additional Data for Weekly Reports:**
```json
{
  "daily_summary": [
    {
      "date": "2025-06-01",
      "day_of_week": "Sunday",
      "completion_rate": 0.75,
      "mood": "good"
    },
    // ... other days
  ],
  "tags_summary": [
    {
      "tag": {"id": 2, "name": "writing", "color": "#3498DB"},
      "count": 5,
      "completed": 3
    },
    // ... other tags
  ]
}
```

## UI Component Data Requirements

### 1. CommitmentCard

**Required Data:**
```json
{
  "id": 1,
  "entity_type": "catchlist_item",
  "entity": {
    "id": 42,
    "content": "Buy groceries",
    "status": "active",
    "tags": [{"id": 1, "name": "errands", "color": "#FF5733"}]
  },
  "due_date": "2025-06-05",
  "time_box": "01:30:00",
  "completed": false
}
```

**API Endpoint:**
- Provided by parent components via `/api/commitments`

**Actions:**
- `PATCH /api/commitments/{id}` (update status, reschedule)
- `DELETE /api/commitments/{id}` (remove commitment)

### 2. TimeframeSelector

**Required Data:**
```json
{
  "current": {
    "type": "day",
    "start_date": "2025-06-05",
    "end_date": "2025-06-05"
  },
  "available_types": ["day", "week", "month"],
  "navigation": {
    "previous": "2025-06-04",
    "next": "2025-06-06"
  }
}
```

**API Endpoint:**
- `GET /api/timeframes/current?type=day&date=2025-06-05`

## Maintaining Frontend-Backend Consistency

### 1. API Response Validation

Implement validation to ensure API responses match frontend expectations:

```python
def validate_commitment_response(commitment_data):
    """Validate commitment response format"""
    required_fields = ['id', 'entity_type', 'entity_id', 'due_date', 'completed']
    for field in required_fields:
        if field not in commitment_data:
            raise ValueError(f"Missing required field: {field}")

    # Validate entity data is included
    if 'entity' not in commitment_data:
        raise ValueError("Missing entity data")
```

### 2. Frontend Component PropTypes

Use TypeScript interfaces or PropTypes to ensure components receive correct data:

```typescript
interface CommitmentProps {
  id: number;
  entity_type: 'catchlist_item' | 'project_task' | 'session';
  entity: {
    id: number;
    [key: string]: any; // Other entity-specific properties
  };
  due_date: string; // YYYY-MM-DD format
  time_box?: string; // HH:MM:SS format, optional
  completed: boolean;
  completed_at?: string; // ISO date string, optional
}

const CommitmentCard: React.FC<CommitmentProps> = (props) => {
  // Component implementation
};
```

### 3. API Versioning

Consider implementing API versioning for major changes:

```
/api/v1/commitments
/api/v2/commitments
```

This allows maintaining backward compatibility while introducing new features.
