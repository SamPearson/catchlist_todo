from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time
import allure


# Selenium does not natively support locating elements by the data-testid attribute.
# so we just convert it to an css_selector locator instead.
# we do this here instead of when defining the locator to avoid needing to spell f"[data-testid='{locator[1]}']")
# correctly for every locator.
def testid_locator(locator_string):
    return By.CSS_SELECTOR, f"[data-testid='{locator_string}']"


class ElementStillPresentException(Exception):
    def __init__(self, message):
        self.message = message


class BasePage:
    """
    Wrapper class for selenium's basic functionality. Includes some methods for
    navigation, element finding, interaction, and waiting operations.
    Actual page objects should inherit from this class, store locators and functions relevant to that app page.
    """

    def __init__(self, driver):
        self.driver = driver

    # ===== Navigation Methods =====
    @allure.step("Navigate to {url}")
    def _visit(self, url):
        """
        Navigate to a URL, handling both absolute and relative paths.
        
        Args:
            url (str): The URL to visit. If not starting with 'http', 
                      the url argument will be appended to driver.base_url
        """
        if url.startswith("http"):
            self.driver.get(url)
        else:
            self.driver.get(self.driver.base_url + url)

    # ===== Element Finding Methods =====
    @allure.step("Find element {locator}")
    def _find(self, locator, timeout=2):
        """
        Find a single element, ensuring it's active before returning.
        
        Args:
            locator: A tuple of (By, value) for element location
            timeout (int): Maximum time to wait for element to be active
            
        Returns:
            WebElement: The found element
            
        Raises:
            NoSuchElementException: If element not found
            AssertionError: If element found but not active
        """
        assert self._is_active(locator, timeout), (
            f"Element {locator} found but not active. "
            f"Diagnostics: {self._get_element_diagnostics(locator)}"
        )
        return self.driver.find_element(*locator)

    @allure.step("Find all elements matching {locator}")
    def _find_all(self, locator):
        """Find all elements matching the locator"""
        assert self._is_active(locator, 2), f"Elements not active: {locator}"
        elements = self.driver.find_elements(*locator)
        if not elements:
            raise NoSuchElementException(f"No elements found: {locator}")
        return elements

    # ===== Element Interaction Methods =====
    @allure.step("Click element {locator}")
    def _click(self, locator):
        """
        Click an element with JavaScript fallback.
        
        Args:
            locator: A tuple of (By, value) for element location
            
        Raises:
            NoSuchElementException: If element not found
            ElementNotInteractableException: If element found but not clickable
        """
        element = self._find(locator)
        try:
            element.click()
        except Exception as e:
            self._log_interaction_failure("click", locator, e)
            self.driver.execute_script("arguments[0].click();", element)

    @allure.step("Type '{input_text}' into element {locator}")
    def _type(self, locator, input_text):
        """Type text into an element"""
        element = self._find(locator)
        element.clear()
        element.send_keys(input_text)

    # ===== Element State Methods =====
    def _is_active(self, locator, timeout=0):
        """
        Check if element is present, visible, and interactive.
        
        Args:
            locator: A tuple of (By, value) for element location
            timeout (int): Maximum time to wait for element to be active
            
        Returns:
            bool: True if element is active, False otherwise
        """
        if timeout > 0:
            try:
                wait = WebDriverWait(self.driver, timeout)
                # First check if element is present and visible using Selenium's built-in methods
                element = wait.until(
                    expected_conditions.presence_of_element_located(locator)
                )
                # Then check if it's enabled
                return element.is_enabled()
            except TimeoutException:
                return False
        else:
            try:
                element = self.driver.find_element(*locator)
                
                # Get element's position and size
                location = element.location
                size = element.size
                
                # Check if element is in viewport
                viewport_height = self.driver.execute_script("return window.innerHeight")
                viewport_width = self.driver.execute_script("return window.innerWidth")
                
                in_viewport = (
                    0 <= location['x'] <= viewport_width and
                    0 <= location['y'] <= viewport_height
                )
                
                # Check if element has size
                has_size = size['height'] > 0 and size['width'] > 0
                
                # Check if element is enabled
                is_enabled = element.is_enabled()
                
                # Get computed style
                computed_style = self.driver.execute_script(
                    "return window.getComputedStyle(arguments[0])",
                    element
                )
                
                # Check if element is visible via CSS
                is_visible_css = (
                    computed_style['display'] != 'none' and
                    computed_style['visibility'] != 'hidden' and
                    float(computed_style['opacity']) > 0
                )
                
                # Log detailed diagnostics if element is not active
                if not (in_viewport and has_size and is_enabled and is_visible_css):
                    self._log_element_state(
                        element,
                        in_viewport=in_viewport,
                        has_size=has_size,
                        is_enabled=is_enabled,
                        is_visible_css=is_visible_css,
                        location=location,
                        size=size,
                        computed_style=computed_style
                    )
                
                return in_viewport and has_size and is_enabled and is_visible_css
                
            except NoSuchElementException:
                return False

    def _log_element_state(self, element, **kwargs):
        """Log detailed information about element state"""
        print("\nElement State Diagnostics:")
        print(f"HTML: {element.get_attribute('outerHTML')}")
        for key, value in kwargs.items():
            print(f"{key}: {value}")
        
        # Take screenshot if in headless mode
        if self.driver.execute_script("return navigator.webdriver"):
            try:
                screenshot_path = f"element_state_{int(time.time())}.png"
                element.screenshot(screenshot_path)
                allure.attach(
                    open(screenshot_path, 'rb').read(),
                    name="element_state_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
                print(f"Screenshot saved to: {screenshot_path}")
            except Exception as e:
                print(f"Failed to take screenshot: {e}")

    # ===== Diagnostic Methods =====
    def _get_element_diagnostics(self, locator):
        """
        Get detailed diagnostic information about an element.
        
        Args:
            locator: A tuple of (By, value) for element location
            
        Returns:
            dict: Diagnostic information including:
                - present: bool
                - visible: bool
                - enabled: bool
                - html: str
                - computed_style: dict
                - position: dict
                - size: dict
        """
        try:
            element = self.driver.find_element(*locator)
            return {
                'present': True,
                'visible': element.is_displayed(),
                'enabled': element.is_enabled(),
                'html': element.get_attribute('outerHTML'),
                'computed_style': self.driver.execute_script(
                    "return window.getComputedStyle(arguments[0])",
                    element
                ),
                'position': element.location,
                'size': element.size,
                'classes': element.get_attribute('class'),
                'attributes': self.driver.execute_script(
                    "return Object.fromEntries(Object.entries(arguments[0].attributes)"
                    ".map(([k,v]) => [v.name, v.value]))",
                    element
                )
            }
        except NoSuchElementException:
            return {
                'present': False,
                'error': 'Element not found'
            }

    def _log_interaction_failure(self, action, locator, exception):
        """Log detailed information about interaction failures"""
        diagnostics = self._get_element_diagnostics(locator)
        allure.attach(
            str(diagnostics),
            name=f"{action}_failure_diagnostics",
            attachment_type=allure.attachment_type.TEXT
        )
        print(f"Failed to {action} element {locator}")
        print(f"Exception: {str(exception)}")
        print(f"Element diagnostics: {diagnostics}")

    # ===== Wait Condition Methods =====
    def _wait_until(self, condition_function, timeout=10, error_message=None):
        """Wait until the provided condition function returns true"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(condition_function)
        except TimeoutException:
            if error_message:
                raise AssertionError(error_message)
            raise TimeoutException(f'Condition not met after {timeout} seconds')

    def wait_for_url(self, condition, value, negate=False, timeout=5):
        """Wait for URL to match condition"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            if condition == 'contains':
                url_condition = expected_conditions.url_contains(value)
            elif condition == 'is':
                url_condition = expected_conditions.url_to_be(value)
            else:
                raise ValueError('Invalid URL condition')

            if negate:
                wait.until_not(url_condition)
            else:
                wait.until(url_condition)
        except TimeoutException:
            raise ElementStillPresentException(
                f'URL condition not met: {condition} {value} = {negate}'
            )

    def _find_children(self, parent, locator):
        children = parent.find_elements(*locator)
        if children:
            return children
        else:
            raise NoSuchElementException(f"No child elements were found with the locator {locator}")

    def _has_children(self, parent, locator):
        children = parent.find_elements(*locator)
        if children:
            return True
        return False

    def _find_child(self, parent, locator):
        return self._find_children(parent, locator)[0]

    def _wait_until_element_gone(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                expected_conditions.invisibility_of_element_located(locator))
        except TimeoutException:
            raise Exception(f'Waited for element to disappear but timed out after {timeout} seconds.'
                            f' - Using locator {locator}')

