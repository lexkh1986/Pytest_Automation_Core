import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *


class WebDriver(object):
    """
        Selenium WebDriver to control the web interface
        @author: Lex.Khuat
    """
    driver = None
    downloadPath = None

    # Private #
    def __init__(self, browser):
        self.browser = browser.lower()

    def __wait__(self, timeout):
        return WebDriverWait(self.driver, timeout)

    # Browser
    def setDownloadPath(self, dirPath):
        """
        Set path for downloaded files
        @param dirPath: directory path
        """
        self.downloadPath = os.path.realpath(dirPath)
        return self

    def launch(self, headless=False):
        """
        Launch the browser
        @note: the webdriver executable path must be setup in PATH environment variable
        @return: self
        """
        if self.downloadPath is None:
            raise WebDriverException('Download Folder Path is not set')

        if self.browser in ('chrome', 'gc', 'google chrome'):
            capabilities = DesiredCapabilities.CHROME
            capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}

            prefs = {'download.default_directory': os.path.abspath(self.downloadPath),
                     'download.directory_upgrade': True,
                     'download.prompt_for_download': False,
                     'safebrowsing.disable_download_protection': True}
            options = webdriver.ChromeOptions()
            options._arguments = ['--disable-plugins', '--disable-extensions', '--incognito']
            options.add_experimental_option('w3c', False)
            options.add_experimental_option('prefs', prefs)
            if headless:
                options.add_argument('--window-size=1600,900')
                options.add_argument('--headless')
            self.driver = webdriver.Chrome(options=options,
                                           desired_capabilities=capabilities,
                                           service_log_path=os.path.devnull)
            if headless:
                self.driver.command_executor._commands["send_command"] \
                    = ("POST", '/session/$sessionId/chromium/send_command')
                params = {'cmd': 'Page.setDownloadBehavior', 'params': {
                    'behavior': 'allow', 'downloadPath': self.downloadPath}}
                self.driver.execute("send_command", params)
            self.driver.execute_script('window.confirm = function(){return true;}')
        elif self.browser in ('ff', 'firefox'):
            self.driver = webdriver.Firefox(service_log_path=os.path.devnull)
        return self

    def quit(self):
        """
        Close the web driver
        @return: self
        """
        self.driver.quit()
        return self

    def clear_all_cookies(self):
        """
        Clear all cookies in browser
        @return: self
        """
        self.driver.delete_all_cookies()
        return self

    def clear_cookie(self, name):
        """
        Clear a specific name cookie in browser
        @param name: name of the cookie
        @return: self
        """
        self.driver.delete_cookie(name)
        return self

    def maximize(self):
        """
        Maximize the current browser
        @return: self
        """
        self.driver.maximize_window()
        return self

    def take_screenshot(self, path, name):
        """
        Take a screenshot of browser
        @param path: path to save screenshot
        @param name: filename
        @return: self
        """
        self.driver.save_screenshot('{}/{}.png'.format(os.path.realpath(path), name))
        return self

    def get_log(self, log_type):
        """
        Return selenium browser log. Only support chrome
        @param log_type: type of log to return
        @return: list of log
        """
        if self.driver.capabilities['browserName'] == 'chrome':
            return self.driver.get_log(log_type)
        return []

    def get_capabilities(self):
        """
        Return the browser capabilities
        @return: dict
        """
        return self.driver.capabilities

    def get_pagesource(self):
        """
        Return current page source
        @return: html source
        """
        return self.driver.page_source

    # Page navigation
    def get(self, url):
        """
        Navigate to a url
        @param url: url to navigate
        @return: self
        """
        self.driver.get(url)
        return self

    def refresh(self):
        """
        Refresh current page
        @return: self
        """
        self.driver.refresh()
        return self

    def forward(self):
        """
        Go forward (after go back)
        @return: self
        """
        self.driver.forward()
        return self

    def back(self):
        """
        Go back to previous page
        @return: self
        """
        self.driver.back()
        return self

    # Element find
    def find(self, locator):
        """
        Find and return matched element
        @param locator: By.By, Expression to find in tuple
        @return: element
        """
        return self.driver.find_element(*locator)

    # Element condition status
    def is_visible(self, locator, timeout=0):
        """
        Check for a duration until an element is visible on UI
        @param locator: xpath expression
        @param timeout: waiting time (seconds)
        @return: bool
        """
        try:
            return self.__wait__(timeout).until(EC.visibility_of_element_located(locator)) is not None
        except WebDriverException as e:
            return False

    def is_invisible(self, locator, timeout=0):
        """
        Check for a duration until an element is invisible on UI
        @rtype: bool
        @param locator: xpath expression
        @param timeout: waiting time (seconds)
        @return: bool
        """
        try:
            return self.__wait__(timeout).until(EC.invisibility_of_element_located(locator)) is not None
        except WebDriverException as e:
            return False

    def is_presented(self, locator, timeout=0):
        """
        Check for a duration until an element is presented on page (it may not be visible)
        @param locator: xpath expression
        @param timeout: waiting time (seconds)
        @return: bool
        """
        try:
            return self.__wait__(timeout).until(EC.presence_of_element_located(locator)) is not None
        except WebDriverException as e:
            return False

    def is_notpresented(self, locator, timeout=0):
        """
        Check for a duration until an element is not presented on page
        @param locator: xpath expression
        @param timeout: waiting time (seconds)
        @return: bool
        """
        try:
            return self.__wait__(timeout).until(EC.presence_of_element_located(locator)) is None
        except WebDriverException as e:
            return False

    def is_clickable(self, locator, timeout=0):
        """
        Check for a duration until an element is clickable on page
        @param locator: xpath expression
        @param timeout: waiting time (seconds)
        @return: bool
        """
        try:
            return self.__wait__(timeout).until(EC.element_to_be_clickable(locator)) is not None
        except WebDriverException as e:
            return False

    def is_checkbox_checked(self, locator):
        """
        Check whether a checkbox is selected or not
        @param locator: xpath expression
        @return: bool
        """
        jsScript = "return arguments[0].checked;"
        return self.driver.execute_script(jsScript, self.find(locator))

    # Get element info
    def get_text(self, locator):
        """
        Return the text value of the element
        @param locator: xpath expression
        @return: string
        """
        return self.find(locator).text

    def get_innertext(self, locator):
        """
        Return the innertext value of the element
        @param locator: xpath expression
        @return: string
        """
        jsScript = 'return arguments[0].innerText;'
        return self.driver.execute_script(jsScript, self.find(locator))

    def get_attribute(self, locator, attribute):
        """
        Return the value of expected attribute from the element
        @param locator: xpath expression
        @param attribute: attribute name to get
        @return:string
        """
        return self.find(locator).get_attribute(attribute)

    def get_value(self, locator):
        """
        Return the value of "value" attribute of the element
        @param locator: xpath expression
        @return: string
        """
        return self.find(locator).get_attribute('value')

    def get_tagname(self, locator):
        """
        Return tagname of the element
        @param locator: xpath expression
        @return: string
        """
        return self.find(locator).tag_name

    def get_html(self, locator):
        """
        Return html source of the element
        @param locator: xpath expression
        @return: string
        """
        return self.find(locator).get_attribute('innerHTML')

    # Set element info
    def set_value(self, locator, value):
        """
        Update the value of "value" attribute of an element to new one
        @param locator: xpath expression
        @param value: new value to set
        """
        self.set_attribute(locator, 'value', value)

    def set_attribute(self, locator, attribute, value):
        """
        Update the value of an expected attribute of an element to new one
        @param locator: xpath expression
        @param attribute: attribute name to set
        @param value: new value to set
        """
        jsScript = "arguments[0].setAttribute('" + attribute + "','" + value + "');"
        self.driver.execute_script(jsScript, self.find(locator))

    def set_text(self, locator, value):
        """
        Update the text value of an element to new one
        @param locator: xpath expression
        @param value: new value to set
        """
        jsScript = "arguments[0].textContent = " + value + ";"
        self.driver.execute_script(jsScript, self.find(locator))

    # Form action
    def input_text(self, locator, text):
        """
        Enter text value into a textbox/text area
        @param locator: xpath expression
        @param text: text value to input
        @return: self
        """
        self.find(locator).send_keys(text)
        return self

    def clear_text(self, locator):
        """
        Clear the current text of element
        @param locator: xpath expression
        @return: self
        """
        self.find(locator).clear()
        return self

    def get_list_all_options(self, locator):
        """
        Return the list of all options from dropdown
        @param locator: xpath expression (must be a select html tag)
        @return: <List>
        """
        return [item.text for item in Select(self.find(locator)).options]

    def get_list_selected_options(self, locator):
        """
        Return the list of selected options (multiple selections dropdown)
        @param locator: xpath expression (must be a select html tag)
        @return: <List>
        """
        return [item.text for item in Select(self.find(locator)).all_selected_options]

    def get_list_selected_option(self, locator):
        """
        Return the the selected option (or first selected option in multiple selections dropdown)
        @param locator: xpath expression (must be a select html tag)
        @return: <String>
        """
        return Select(self.find(locator)).first_selected_option.text

    def select_list_by_index(self, locator, index):
        """
        Select an option from dropdown list by option index
        @param locator: xpath expression (must be a select html tag)
        @param index: index of the option. Started by 0
        @return: self
        """
        Select(self.find(locator)).select_by_index(int(index))
        return self

    def select_list_by_value(self, locator, value):
        """
        Select an option from dropdown list by option value
        @param locator: xpath expression (must be a select html tag)
        @param value: value of the option
        @return: self
        """
        Select(self.find(locator)).select_by_value(str(value))
        return self

    def select_list_by_label(self, locator, name):
        """
        Select an option from dropdown list by option text name
        @param locator: xpath expression (must be a select html tag)
        @param name: text value of the option
        @return: self
        """
        Select(self.find(locator)).select_by_visible_text(str(name))
        return self

    def select_checkbox(self, locator, value):
        """
        Check/uncheck a checkbox
        @param locator: xpath expression
        @param value: True/False value for ON/OFF indicating
        @return: self
        """
        if self.is_checkbox_checked(locator) != value:
            self.click()
        return self

    # Element interactive
    def click(self, locator):
        """
        Click on an element
        @param locator: xpath expression
        @return: self
        """
        self.find(locator).click()
        return self

    def focus(self, locator):
        """
        Focus on element
        @param locator: xpath expression
        @return: self
        """
        self.find(locator).send_keys(Keys.NULL)
        return self

    def drag_and_drop(self, source, target):
        # TODO
        return self

    def drag_and_drop_by_offset(self, source, xoffset, yoffset):
        # TODO
        return self

    # Script
    def execute_javascript(self, script):
        """
        Execute a javascript on current page
        @param script: script to run
        @return: executed status
        """
        return self.driver.execute_script(script)

    def execute_async_javascript(self, script):
        """
        Execute an async javascript on current page
        @param script: script to run
        @return: executed status
        """
        return self.driver.execute_async_script(script)
