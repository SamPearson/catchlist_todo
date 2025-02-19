from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


# Selenium does not natively support locating elements by the data-testid attribute.
# so we just convert it to an xpath locator instead.
# we do this instead of just using an xpath locator to avoid needing to spell f"[data-testid='{locator[1]}']")
# correctly for every locator.
def testid_locator(locator_string):
    return By.XPATH, f"//*[@data-testid='{locator_string}']"


class ElementStillPresentException(Exception):
    def __init__(self, message):
        self.message = message


class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def _visit(self, url):
        if url.startswith("http"):
            self.driver.get(url)
        else:
            self.driver.get(self.driver.base_url + url)

    def wait_for_url(self, condition, value, negate=False, timeout=5):
        # Waits until the current URL is, isn't, contains, or doesn't contain the given value
        try:
            wait = WebDriverWait(self.driver, timeout)

            if condition == 'contains':
                url_condition = expected_conditions.url_contains(value)
            elif condition == 'is':
                url_condition = expected_conditions.url_to_be(value)
            else:
                raise ValueError('Invalid URL Condition Provided')

            if negate:
                wait.until_not(url_condition)
            else:
                wait.until(url_condition)

        except TimeoutException:
            raise ElementStillPresentException(f'waited for url {condition} {value} = {negate} , '
                                               f'but timed out after {timeout} seconds')

    def _find(self, locator, timeout=2):
        assert self._is_active(locator, timeout), f"Attempted to find element with the locator {locator}, but could not"
        return self.driver.find_element(*locator)

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

    def _find_all(self, locator):
        assert self._is_active(locator, 2), f"Attempted to find elements with the locator {locator}, but could not"
        elements = self.driver.find_elements(*locator)
        if elements:
            return elements
        else:
            raise NoSuchElementException(f"No elements were found with the locator {locator}")

    def _click(self, locator):
        self._find(locator).click()

    def _type(self, locator, input_text):
        self._find(locator).send_keys(input_text)

    def _is_active(self, locator, timeout=0):
        """Tests whether an element is present, visible, and interactive"""
        if timeout > 0:
            try:
                wait = WebDriverWait(self.driver, timeout)
                wait.until(
                    expected_conditions.element_to_be_clickable(locator) and
                    expected_conditions.visibility_of_element_located(locator))
            except TimeoutException:
                return False
            return True
        else:
            try:
                return self._find(locator).is_enabled()
            except NoSuchElementException:
                return False

    def _is_displayed(self, locator, timeout=0):
        """Tests whether an element is present, whether visible/interactive or not"""
        if timeout > 0:
            try:
                wait = WebDriverWait(self.driver, timeout)
                wait.until(
                    expected_conditions.presence_of_element_located(locator))
            except TimeoutException:
                return False
            return True
        else:
            try:
                return self._find(locator).is_displayed()
            except NoSuchElementException:
                return False

    def _wait_until_element_gone(self, locator, timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(
                expected_conditions.invisibility_of_element_located(locator))
        except TimeoutException:
            raise Exception(f'Waited for element to disappear but timed out after {timeout} seconds.'
                            f' - Using locator {locator}')

