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
def locator_from_testid(locator_string):
    return By.CSS_SELECTOR, f"[data-testid='{locator_string}']"

def _check_element_visibility(driver, element):
    """
    Check if an element is visible using JavaScript
    
    Args:
        driver: WebDriver instance
        element: WebElement to check
        
    Returns:
        bool: True if element is visible, False otherwise
    """
    return driver.execute_script("""
        var elem = arguments[0];
        var rect = elem.getBoundingClientRect();
        return (
            rect.width > 0 &&
            rect.height > 0 &&
            window.getComputedStyle(elem).display !== 'none' &&
            window.getComputedStyle(elem).visibility !== 'hidden' &&
            window.getComputedStyle(elem).opacity !== '0'
        );
    """, element)


class ElementIsVisible:
    """
    Custom expected condition for WebDriverWait.
    Checks if element is present and visible.
    """
    def __init__(self, locator):
        self.locator = locator
    
    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            return _check_element_visibility(driver, element)
        except (NoSuchElementException, StaleElementReferenceException):
            return False


class ElementIsActive:
    """
    Custom expected condition for WebDriverWait.
    Checks if element is present, visible, and enabled (interactable).
    """
    def __init__(self, locator):
        self.locator = locator
    
    def __call__(self, driver):
        try:
            element = driver.find_element(*self.locator)
            is_visible = _check_element_visibility(driver, element)
            is_enabled = element.is_enabled()
            return is_visible and is_enabled
        except (NoSuchElementException, StaleElementReferenceException):
            return False


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


    def _wait_for_url(self, condition, value, negate=False, timeout=5):
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
            # Log the failure and try JavaScript click
            self._log_interaction_failure("click", locator, e)
            
            # Try to scroll element into view first
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Try JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", element)
            except Exception as js_e:
                # If JavaScript click fails, raise the original exception
                raise e from js_e  # Chain the exceptions to preserve both error contexts


    @allure.step("Type '{input_text}' into element {locator}")
    def _type(self, locator, input_text):
        """Type text into an element"""
        element = self._find(locator)
        element.clear()
        element.send_keys(input_text)


    def _take_screenshot(self, name="element_state"):
        """Take a screenshot and attach it to the Allure report"""
        try:
            screenshot = self.driver.get_screenshot_as_png()
            allure.attach(
                screenshot,
                name=f"{name}_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")


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
                wait.until(ElementIsActive(locator))
                return True

            except TimeoutException:
                # Take screenshot on timeout and log diagnostics
                self._take_screenshot(f"timeout_checking_{locator[1]}")
                
                # Try to get diagnostics if element exists but isn't active
                try:
                    element = self.driver.find_element(*locator)
                    is_visible = _check_element_visibility(self.driver, element)
                    is_enabled = element.is_enabled()
                    
                    self._log_element_state(
                        element,
                        is_visible=is_visible,
                        is_enabled=is_enabled,
                        rect=self.driver.execute_script(
                            "return arguments[0].getBoundingClientRect();",
                            element
                        )
                    )
                except NoSuchElementException:
                    print(f"Element not found: {locator}")
                
                return False
        else:
            try:
                element = self.driver.find_element(*locator)
                is_visible = _check_element_visibility(self.driver, element)
                is_enabled = element.is_enabled()
                
                if not (is_visible and is_enabled):
                    self._log_element_state(
                        element,
                        is_visible=is_visible,
                        is_enabled=is_enabled,
                        rect=self.driver.execute_script(
                            "return arguments[0].getBoundingClientRect();",
                            element
                        )
                    )
                    # Take screenshot after failed visibility check
                    self._take_screenshot(f"failed_visibility_check_{locator[1]}")
                
                return is_visible and is_enabled
            except NoSuchElementException:
                # Take screenshot when element not found
                self._take_screenshot(f"element_not_found_{locator[1]}")
                return False

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
        
        # Log to console
        print("\nElement State Diagnostics:")
        for key, value in diagnostic_info.items():
            print(f"{key}: {value}")
        
        try:
            # Take screenshot of the entire page
            screenshot = self.driver.get_screenshot_as_png()
            
            # Add to Allure report
            allure.attach(
                screenshot,
                name="element_state_screenshot",
                attachment_type=allure.attachment_type.PNG
            )
            
            # Add diagnostic info to Allure report
            allure.attach(
                str(diagnostic_info),
                name="element_state_diagnostics",
                attachment_type=allure.attachment_type.TEXT
            )
        except Exception as e:
            print(f"Failed to capture screenshot: {e}")


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



    def _wait_until_element_gone(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                expected_conditions.invisibility_of_element_located(locator))
        except TimeoutException:
            raise Exception(f'Waited for element to disappear but timed out after {timeout} seconds.'
                            f' - Using locator {locator}')

    def _is_displayed(self, locator, timeout=2):
        """
        Check if an element is displayed.
        
        Args:
            locator: A tuple of (By, value) for element location
            timeout (int): Maximum time to wait for element to be present
            
        Returns:
            bool: True if element is displayed, False otherwise
        """
        try:
            element = self._find(locator, timeout)
            return element.is_displayed()
        except (NoSuchElementException, AssertionError):
            return False


    def _wait_for_alert(self, timeout=5):
        """
        Wait for an alert to be present.
        
        Args:
            timeout (int): Maximum time to wait for alert
            
        Returns:
            Alert: The alert object if found
            
        Raises:
            TimeoutException: If no alert appears within timeout
        """
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(expected_conditions.alert_is_present())

    def _get_alert_text(self, timeout=5):
        """
        Get the text from an alert.
        
        Args:
            timeout (int): Maximum time to wait for alert
            
        Returns:
            str: The alert text
        """
        alert = self._wait_for_alert(timeout)
        return alert.text

    def _accept_alert(self, timeout=5):
        """
        Accept (click OK on) an alert.
        
        Args:
            timeout (int): Maximum time to wait for alert
        """
        alert = self._wait_for_alert(timeout)
        alert.accept()

    def _dismiss_alert(self, timeout=5):
        """
        Dismiss (click Cancel on) an alert.
        
        Args:
            timeout (int): Maximum time to wait for alert
        """
        alert = self._wait_for_alert(timeout)
        alert.dismiss()

