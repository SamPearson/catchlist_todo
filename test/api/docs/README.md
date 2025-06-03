# API Testing Documentation

## Overview
The API testing framework uses Newman (Postman's command-line collection runner) to execute API tests against different environments. This approach allows for consistent testing across development, staging, and production environments with minimal configuration changes.

## Architecture

### Core Components

#### 1. Postman Collections
JSON files containing organized API requests and tests:
- Endpoints are grouped by functionality
- Each request includes test scripts for validation
- Environment variables used for flexibility

#### 2. Environment Files
JSON files with environment-specific variables:
- Base URLs
- Authentication credentials
- Test data values

#### 3. Newman Runner
Command-line tool to execute collections:
- Runs all tests in a collection
- Generates test reports
- Can be integrated into CI/CD pipelines

## Getting Started

### Setup
```bash
# Install Node.js and npm
sudo apt update
sudo apt install nodejs npm

# Install Newman globally
npm install -g newman

# Optional: Install HTML reporter
npm install -g newman-reporter-htmlextra
```

### Configuration
Edit the environment files in `test/api/environments/` to match your deployment:
- `local_env.json`: For local development testing
- `staging_env.json`: For staging environment testing
- `production_env.json`: For production environment testing

### Running Tests
```bash
# Run with local environment
./test_local.sh

# Or run directly with Newman
newman run collection.json -e environments/local_env.json

# Generate HTML report
newman run collection.json -e environments/local_env.json -r htmlextra
```

## Test Organization

The API tests are organized in the collection by resource type:
- Authentication endpoints
- User management endpoints
- Feature-specific endpoints

Each request includes:
1. URL and parameters
2. Headers and authentication
3. Request body (if applicable)
4. Test scripts for validating responses

## Documentation Sections

1. [Setup Guide](setup_guide.md)
   - Detailed environment configuration
   - Installation steps
   - Configuration options

2. [Collection Structure](collection_structure.md)
   - Understanding the collection organization
   - Endpoint grouping
   - Request dependencies

3. [Writing Tests](writing_tests.md)
   - Test script structure
   - Common assertions
   - Using environment variables

4. [CI/CD Integration](ci_cd_integration.md)
   - Jenkins integration
   - Automated test execution
   - Report generation

5. [Best Practices](best_practices.md)
   - Test independence
   - Error handling
   - Performance considerations

## Environment Files

Environment files use the standard Postman format:
```json
{
  "id": "e1078bac-5906-4b99-903b-453d3619576e",
  "name": "Environment Name",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:5001",
      "type": "default",
      "enabled": true
    },
    {
      "key": "username",
      "value": "test_user",
      "type": "default",
      "enabled": true
    }
  ]
}
```

## Example Test

```javascript
// Example Postman test script
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response contains auth token", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.access_token).to.exist;

    // Store token for subsequent requests
    pm.environment.set("auth_token", jsonData.access_token);
});
```