# API Test Collection Structure

## Overview
The API test collection is organized into folders that represent logical groupings of endpoints. This organization helps maintain a clear structure as the API grows and evolves.

## Collection Organization

```
Personal Development Task Manager API Tests
├── Auth
│   ├── Register
│   ├── Login
│   ├── Logout
│   └── User Info
├── Catchlist Items
│   ├── Get All Items
│   ├── Create Item
│   ├── Get Single Item
│   ├── Update Item
│   └── Delete Item
├── Projects
│   ├── Get All Projects
│   ├── Create Project
│   ├── Get Single Project
│   ├── Update Project
│   ├── Delete Project
│   ├── Project Tasks
│   │   ├── Get All Tasks
│   │   ├── Create Task
│   │   ├── Update Task
│   │   └── Delete Task
├── Routines
│   ├── Get All Routines
│   ├── Create Routine
│   ├── Get Single Routine
│   ├── Update Routine
│   ├── Delete Routine
│   ├── Sessions
│   │   ├── Get Sessions
│   │   ├── Create Session
│   │   └── Delete Session
├── Commitments
│   ├── Get All Commitments
│   ├── Create Commitment
│   ├── Update Commitment
│   └── Delete Commitment
├── Tags
│   ├── Get All Tags
│   ├── Create Tag
│   ├── Delete Tag
│   └── Tag Association
└── Health Check
```

## Request Dependencies

Many API requests depend on previous requests. The collection handles these dependencies using environment variables:

1. **Authentication Flow**:
   - Register a user
   - Login to get an auth token
   - Store token in `auth_token` variable
   - Subsequent requests use the token in Authorization header

2. **Entity Creation Flow**:
   - Create an entity (e.g., project)
   - Store ID in variable (e.g., `project_id`)
   - Use ID in subsequent requests (get, update, delete)

## Request Structure

### Example Request: Create Catchlist Item

```json
{
  "name": "Create Catchlist Item",
  "request": {
    "method": "POST",
    "header": [
      {
        "key": "Content-Type",
        "value": "application/json"
      },
      {
        "key": "Authorization",
        "value": "Bearer {{auth_token}}"
      }
    ],
    "body": {
      "mode": "raw",
      "raw": "{\n  \"content\": \"Buy groceries\"\n}"
    },
    "url": {
      "raw": "{{protocol}}://{{host}}{{port}}/api/catchlist-items",
      "protocol": "{{protocol}}",
      "host": ["{{host}}"],
      "port": "{{port}}",
      "path": ["api", "catchlist-items"]
    }
  },
  "response": []
}
```

### Test Scripts

Each request includes test scripts to validate responses:

```javascript
// Test script for Create Catchlist Item
pm.test("Status code is 201", function () {
    pm.response.to.have.status(201);
});

pm.test("Response has correct structure", function () {
    var jsonData = pm.response.json();

    pm.expect(jsonData).to.have.property("id");
    pm.expect(jsonData).to.have.property("content");
    pm.expect(jsonData).to.have.property("created_at");
    pm.expect(jsonData).to.have.property("status");

    // Store ID for later requests
    pm.environment.set("catchlist_item_id", jsonData.id);
});

pm.test("Content matches request", function () {
    var jsonData = pm.response.json();
    var requestData = JSON.parse(pm.request.body.raw);

    pm.expect(jsonData.content).to.equal(requestData.content);
});
```

## Pre-request Scripts

Some requests use pre-request scripts to prepare data or set up conditions:

```javascript
// Pre-request script for Create Catchlist Item with Random Data
// Generate random content to avoid conflicts
pm.variables.set("random_content", "Task " + Math.random().toString(36).substring(2, 10));
```

## Collection Variables

The collection uses the following types of variables:

1. **Environment Variables**: Server-specific values
   - `protocol` (http/https)
   - `host` (server hostname)
   - `port` (server port)

2. **Dynamic Variables**: Set during test execution
   - `auth_token`: Authentication token
   - Entity IDs: `catchlist_item_id`, `project_id`, etc.

3. **Data Variables**: Test-specific data
   - `username`, `password`
   - `random_content`

## Special Request Types

### 1. Setup Requests

Requests that prepare the environment for testing:
- User registration
- Login to obtain token
- Create base entities

### 2. Cleanup Requests

Requests that clean up after tests:
- Delete created entities
- Logout to invalidate token

### 3. Negative Tests

Requests that test error handling:
- Invalid authentication
- Missing required fields
- Invalid data formats

## Adding New Tests

When adding new endpoints to the collection:

1. Place in the appropriate folder based on entity type
2. Follow the established naming convention
3. Include proper authorization headers
4. Write comprehensive test scripts
5. Handle dependencies with environment variables
6. Add both positive and negative test cases
