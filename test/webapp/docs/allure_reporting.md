# Allure Reporting Integration

## Overview
Allure is a flexible, lightweight multi-language test reporting tool that produces detailed and interactive reports. This framework integrates Allure to provide comprehensive test reports with screenshots, logs, and detailed step information.

## Key Features

1. **Step-by-Step Reporting**: Each test action is logged as a step in the report
2. **Automatic Screenshots**: Captures screenshots on test failures
3. **Element State Diagnostics**: Detailed logging of element state during test execution
4. **Environment Information**: Test environment details included in reports
5. **Failure Analysis**: Comprehensive failure information for debugging

## Configuration

### Pytest Configuration

The Allure integration is configured in `conftest.py`:

```python
# Allure reporting hooks
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    result = outcome.get_result()

    # Add test result to Allure report
    if result.when == "call":
        if result.failed:
            allure.attach(
                str(result.longrepr),
                name="failure_details",
                attachment_type=allure.attachment_type.TEXT
            )

    setattr(item, "result_" + result.when, result)
```

### Screenshot Capture

Screenshots are automatically captured on test failures:

```python
@pytest.fixture
def driver(request):
    driver_ = setup_webdriver(request)

    def quit_browser():
        try:
            # Take screenshot on test failure
            if request.node.result_call.failed:
                allure.attach(
                    driver_.get_screenshot_as_png(),
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
        finally:
            driver_.quit()

    request.addfinalizer(quit_browser)
    return driver_
```

## Test Decoration

### Step Annotation

Test steps are annotated using the `@allure.step` decorator:

```python
class BasePage:
    # ...

    @allure.step("Navigate to {url}")
    def _visit(self, url):
        # Method implementation

    @allure.step("Click element {locator}")
    def _click(self, locator):
        # Method implementation

    @allure.step("Type '{input_text}' into element {locator}")
    def _type(self, locator, input_text):
        # Method implementation
```

### Environment Information

Environment information is added to the report:

```python
@pytest.fixture
def driver(request):
    driver_ = setup_webdriver(request)

    # Add environment information to Allure report
    allure.dynamic.description_html(f"""
        <h3>Test Environment</h3>
        <p><b>Browser:</b> Chrome</p>
        <p><b>Headless:</b> {request.config.getoption("--headless")}</p>
        <p><b>Environment:</b> {request.config.getoption("--env")}</p>
    """)

    # ...
```

## Diagnostic Information

### Element State Logging

Detailed element state information is captured and added to the report:

```python
def _log_element_state(self, element, **kwargs):
    """Log detailed information about element state"""
    # Create a detailed diagnostic message
    diagnostic_info = {
        'html': element.get_attribute('outerHTML'),
        'location': element.location,
        'size': element.size,
        'classes': element.get_attribute('class'),
        'attributes': self.driver.execute_script(
            "return Object.fromEntries(Object.entries(arguments[0].attributes)"
            ".map(([k,v]) => [v.name, v.value]))",
            element
        ),
        **kwargs
    }

    # Add to Allure report
    allure.attach(
        str(diagnostic_info),
        name="element_state_diagnostics",
        attachment_type=allure.attachment_type.TEXT
    )
```

## Running Tests with Allure

### Command Line Options

```bash
# Run tests with Allure reporting
pytest --env=local_web_env.json --alluredir=./allure-results

# Generate and view the report
allure serve ./allure-results
```

### CI/CD Integration

In Jenkins, you can use the Allure Jenkins plugin to generate and publish reports:

```groovy
// Jenkinsfile example
pipeline {
    stages {
        stage('Test') {
            steps {
                sh 'pytest --env=staging_web_env.json --alluredir=./allure-results'
            }
            post {
                always {
                    allure([
                        includeProperties: false,
                        jdk: '',
                        properties: [],
                        reportBuildPolicy: 'ALWAYS',
                        results: [[path: 'allure-results']]
                    ])
                }
            }
        }
    }
}
```

## Report Analysis

### Main Dashboard

The Allure report provides a main dashboard with:
- Test execution summary
- Categorized failures
- Duration statistics
- Environment information

### Test Cases

Each test case report includes:
- Step-by-step execution log
- Parameter values
- Failure details (if applicable)
- Attachments (screenshots, logs)

### Troubleshooting

When analyzing failures:
1. Check the failure message and stack trace
2. Examine the screenshot at the point of failure
3. Review element state diagnostics
4. Look at the step-by-step execution log

## Custom Allure Features

### Custom Categories

You can define custom failure categories in `allure-categories.json`:

```json
[
  {
    "name": "Element not found",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*NoSuchElementException.*"
  },
  {
    "name": "Timeout",
    "matchedStatuses": ["failed"],
    "messageRegex": ".*TimeoutException.*"
  }
]
```

### Custom Test Properties

Add custom properties to test reports:

```python
@allure.title("Login with valid credentials")
@allure.description("Verify that users can log in with valid credentials")
@allure.severity(allure.severity_level.CRITICAL)
@allure.feature("Authentication")
@allure.story("Login")
@pytest.mark.smoke
def test_login_with_valid_credentials(driver, test_user_credentials):
    # Test implementation
```