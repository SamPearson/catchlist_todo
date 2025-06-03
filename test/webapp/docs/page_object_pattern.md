# Page Object Pattern

## Overview
The Page Object Model (POM) is a design pattern used in test automation to create an object repository for web UI elements. This pattern creates a clean separation between test code and page-specific code such as locators and methods.

## Framework Architecture

### Class Hierarchy

```
BasePage
  ├── BaseAppPage
      ├── LoginPage
      ├── RegistrationPage
      ├── AccountPage
      ├── DeskPage
      └── ... other page objects
```

## Base Classes

### BasePage

The `BasePage` class provides a wrapper around Selenium WebDriver with enhanced functionality:

```python
class BasePage:
    def __init__(self, driver):
        self.driver = driver

    # Navigation methods
    def _visit(self, url):
        # Navigates to URL with proper base URL handling

    # Element finding methods
    def _find(self, locator, timeout=2):
        # Finds element with active state verification

    def _find_all(self, locator):
        # Finds all matching elements

    # Element interaction methods
    def _click(self, locator):
        # Clicks element with JavaScript fallback

    def _type(self, locator, input_text):
        # Types text into element

    # Wait conditions
    def _wait_until(self, condition_function, timeout=10):
        # Waits for custom condition

    def wait_for_url(self, condition, value, negate=False, timeout=5):
        # Waits for URL to match condition
```

### BaseAppPage

The `BaseAppPage` extends `BasePage` with application-specific elements and behaviors:

```python
class BaseAppPage(BasePage):
    # Common locators across app pages
    home_link_locator = testid_locator("home-link")
    login_link_locator = testid_locator("login-link")
    logout_link_locator = testid_locator("logout-link")
    register_link_locator = testid_locator("register-link")

    # Common methods
    def navigate_to_home(self):
        self._click(self.home_link_locator)
```

## Creating Page Objects

### Step 1: Define Locators

Define element locators at the class level using descriptive names:

```python
class LoginPage(BaseAppPage):
    # Locators
    username_input_locator = testid_locator("username-input")
    password_input_locator = testid_locator("password-input")
    login_button_locator = testid_locator("login-button")
    error_message_locator = testid_locator("login-error")
```

### Step 2: Implement Page-Specific Methods

Create methods that represent user actions on the page:

```python
class LoginPage(BaseAppPage):
    # Locators...

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/login")

    def login(self, username, password):
        self._type(self.username_input_locator, username)
        self._type(self.password_input_locator, password)
        self._click(self.login_button_locator)

    def get_error_message(self):
        return self._find(self.error_message_locator).text
```

### Step 3: Use in Tests

Use the page object in test files:

```python
def test_login(driver, test_user_credentials):
    login_page = LoginPage(driver)
    login_page.login(
        test_user_credentials["username"],
        test_user_credentials["password"]
    )

    # Assert successful login
    assert "desk" in driver.current_url
```

## Best Practices

### Locator Strategies

1. **Use Data Attributes**: Prefer `data-testid` attributes for test stability
   ```python
   # Helper function in BasePage
   def testid_locator(locator_string):
       return By.CSS_SELECTOR, f"[data-testid='{locator_string}']"
   ```

2. **Descriptive Locator Names**: Use clear, descriptive names for locators
   ```python
   # Good
   submit_button_locator = testid_locator("submit-button")

   # Avoid
   btn1 = testid_locator("btn1")
   ```

3. **Locator Hierarchy**: Organize locators logically from top to bottom of page

### Page Methods

1. **Action-Based Methods**: Methods should represent user actions
   ```python
   # Good
   def submit_form(self, data):
       self._type(self.name_input, data["name"])
       self._type(self.email_input, data["email"])
       self._click(self.submit_button)

   # Avoid
   def fill_name_and_click_submit(self, name):
       # Too specific and not reusable
   ```

2. **Return Values**: Methods should return new page objects when navigation occurs
   ```python
   def submit_form(self):
       self._click(self.submit_button)
       return ConfirmationPage(self.driver)
   ```

3. **Validation Methods**: Include methods to verify page state
   ```python
   def is_error_displayed(self):
       return self._is_displayed(self.error_message)

   def get_success_message(self):
       return self._find(self.success_message).text
   ```

## Example Complete Page Object

```python
class RegistrationPage(BaseAppPage):
    # Locators
    username_input = testid_locator("register-username")
    password_input = testid_locator("register-password")
    confirm_password_input = testid_locator("register-confirm-password")
    register_button = testid_locator("register-submit")
    error_message = testid_locator("register-error")

    def __init__(self, driver):
        super().__init__(driver)
        self._visit("/register")

    def register_new_user(self, username, password):
        """Register a new user and return LoginPage"""
        self._type(self.username_input, username)
        self._type(self.password_input, password)
        self._type(self.confirm_password_input, password)
        self._click(self.register_button)
        return LoginPage(self.driver)

    def attempt_register_with_mismatched_passwords(self, username, password, confirm_password):
        """Attempt registration with mismatched passwords"""
        self._type(self.username_input, username)
        self._type(self.password_input, password)
        self._type(self.confirm_password_input, confirm_password)
        self._click(self.register_button)

    def is_error_displayed(self):
        """Check if error message is displayed"""
        return self._is_displayed(self.error_message)

    def get_error_message(self):
        """Get error message text"""
        return self._find(self.error_message).text
```