# WebApp Testing Framework Documentation

## Overview
This testing framework provides a robust solution for end-to-end testing of the webapp using Python, Pytest, and Selenium WebDriver with Allure reporting integration. The framework follows the Page Object Model pattern for better maintainability and includes extensive error handling and debugging capabilities.

## Architecture

### Core Components

#### 1. Base Classes
- **BasePage**: Foundation class with enhanced Selenium operations
  - Element finding and interaction (click, type, etc.)
  - Wait conditions and synchronization
  - Detailed error diagnostics with screenshots
  - JavaScript execution fallbacks

- **BaseAppPage**: Application-specific extension with common elements
  - Navigation links (home, login, logout, register)
  - Common app behaviors

#### 2. Page Objects
Individual page implementations that inherit from BaseAppPage:
- LoginPage
- RegistrationPage
- AccountPage
- And more for each application feature

#### 3. Test Infrastructure
- **Environment Management**: Flexible configuration using Postman-compatible environment files
- **Test Fixtures**: User creation, login, and cleanup
- **Allure Integration**: Detailed test reporting with screenshots and diagnostics

## Key Features

### 1. Robust Element Interaction
- Automatic waiting for elements to be active
- JavaScript fallbacks for element interactions
- Detailed failure diagnostics

### 2. Test User Management
- Automatic user creation before test suite
- Automatic login for authenticated tests
- Automatic cleanup after tests complete

### 3. Comprehensive Reporting
- Step-by-step test execution logs
- Screenshots on failures
- Element state diagnostics
- Detailed error information

## Getting Started

### Setup
```bash
# On the deploy server
# 1. Install Google Chrome
sudo apt-get update
sudo apt-get install -y wget gnupg
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Edit environment files in test/webapp/environments
```

### Running Tests
```bash
# Run smoke tests using local environment
pytest -m smoke --env=local_web_env.json

# Run all tests
pytest --env=local_web_env.json

# Run with Allure reporting
pytest --env=local_web_env.json --alluredir=./allure-results
allure serve ./allure-results
```

## Test Organization

### Test Markers
Tests are organized using pytest markers:
- `smoke`: Critical path tests
- `regression`: Full test suite
- `devtest`: For test development (not run in CI)

Register new markers in `pytest.ini`.

### Test Structure
Typical test structure:
```python
@pytest.mark.smoke
def test_login_with_valid_credentials(driver, test_user_credentials):
    # Arrange
    login_page = LoginPage(driver)

    # Act
    login_page.login(
        test_user_credentials["username"],
        test_user_credentials["password"]
    )

    # Assert
    assert "desk" in driver.current_url
```

## Documentation Sections

1. [Setup Guide](setup_guide.md)
   - Detailed environment configuration
   - Installation steps
   - Configuration options

2. [Page Object Pattern](page_object_pattern.md)
   - Creating page objects
   - Best practices for locators
   - Implementing page behaviors

3. [Allure Reporting](allure_reporting.md)
   - Configuring Allure
   - Test decoration
   - Report analysis

4. [Writing Tests](writing_tests.md)
   - Test case structure
   - Using fixtures
   - Assertions and verifications

5. [Best Practices](best_practices.md)
   - Locator strategies
   - Error handling
   - Test organization

## Environment Files

The framework uses Postman-compatible environment files containing:
- `protocol`: HTTP or HTTPS
- `host`: Server hostname
- `port`: Server port

These values are used to construct the base URL for tests.

