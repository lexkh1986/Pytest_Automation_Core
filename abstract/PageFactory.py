import time
from core.abstract.BaseFactory import BaseFactory
from core.libs.WebDriver import WebDriver


class Page(object):
    """
    Web abstract interface class defines a webpage
    """

    # ------ Private methods -------
    def __init__(self, driver: WebDriver):
        if not isinstance(driver, WebDriver):
            raise ValueError('Driver argument must be a WebDriver class')
        self.__domain = None
        self.__driver = driver
        self.__timeout = 10

    def __getDomain(self):
        return self.__domain

    def __setDomain(self, domain):
        self.__domain = domain

    def __getTimeout(self):
        return self.__timeout

    def __setTimeout(self, timeout):
        self.__timeout = timeout

    def __getDriver(self):
        return self.__driver

    def __setDriver(self, driver):
        if not isinstance(driver, WebDriver):
            raise ValueError('Driver argument must be a WebDriver class')
        self.__driver = driver

    domain = property(__getDomain, __setDomain)
    driver = property(__getDriver, __setDriver)
    timeout = property(__getTimeout, __setTimeout)

    # ------ Public methods -------
    def go(self, uri=''):
        """
        Navigate to the expected page
        @param uri: url address of the page after the domain
        """
        self.driver.get('%s/%s' % (self.domain, uri))

    def sleep(self, timeout=1):
        """
        Wait for second(s) before doing next action
        @param timeout: in second
        """
        time.sleep(timeout)
        return self


class Environment(object):
    """
    Object inherited class defines a test environment
    """

    # ------ Private methods -------
    def __init__(self, type: str, domain: str):
        self.__type = type
        self.__domain = domain

    def __getType(self):
        return self.__type

    def __getDomain(self):
        return self.__domain

    type = property(__getType)
    domain = property(__getDomain)


class PageFactory(BaseFactory):
    """
    Object inherited class defines a POM structure simulate a web system to test
    PageFactory object holds:
    - An attached WebDriver engine to produce & control test pages (inherited Page class)
    - An attached test environment objects which holds url domain and environment type to test
    @author: lex.khuat
    """
    __environment = None
    __engine = None

    # ------ Private methods -------
    def __init__(self, siteName: str):
        self.siteName = siteName

    def __getEnvironment(self):
        return self.__environment

    def __getEngine(self):
        return self.__engine

    def __setEnvironment(self, environment: Environment):
        if not isinstance(environment, Environment):
            raise ValueError('%s argument must be an %s classType' % (environment, Environment))
        self.__environment = environment

    def __setEngine(self, engine: WebDriver):
        if not isinstance(engine, WebDriver):
            raise ValueError('%s argument must be a %s classType' % (engine, WebDriver))
        self.__engine = engine

    engine = property(__getEngine, __setEngine)
    environment = property(__getEnvironment, __setEnvironment)

    # ------ Public methods -------
    def switchEnv(self, envObj: Environment):
        """
        Switch the current attached environment into a new stored one
        Also update domain of all belonged pages
        @param envObj: environment object to switch
        @return: self
        """
        if envObj not in self.storedEnvironments:
            raise LookupError('Environment object is not stored first' % envObj)
        self.environment = envObj
        for page in self.storedPages:
            page.domain = envObj.domain
        return self

    def switchEngine(self, engineObj: WebDriver):
        """
        Switch the current attached WedDriver engine into a new stored one
        Also update driver of all belonged pages
        @param engineObj: WebDriver object to switch
        @return: self
        """
        if engineObj not in self.storedEngines:
            raise LookupError('Environment object is not stored first' % engineObj)
        self.engine = engineObj
        for page in self.storedPages:
            page.driver = engineObj
        return self

    def storedPages(self):
        """
        Return all stored pages
        @return: <List>Page
        """
        return self.getObj(Page)

    def storedEnvironments(self):
        """
        Return all stored environments
        @return: <List>Environment
        """
        return self.getObj(Environment, exclude=[self.environment])

    def storedEngines(self):
        """
        Return all stored WebDriver
        @return: <List>WebDriver
        """
        return self.getObj(WebDriver, exclude=[self.engine])

    storedPages = property(storedPages)
    storedEngines = property(storedEngines)
    storedEnvironments = property(storedEnvironments)

    def addPage(self, pageName: str, classType: Page, kwargs={}):
        """
        Produce and store a new page object (inherited Page class)
        @param pageName: name of the new page to store
        @param classType: inherited Page classname
        @param kwargs: more inherited class init kwargs
        @return: <Page>newPage
        """
        if self.environment is None:
            raise ValueError('Please set environment before adding new page')
        if self.engine is None:
            raise ValueError('Please set engine before adding new page')

        kwargs.update({'driver': self.__engine})
        newPage = classType(**kwargs)
        if not isinstance(newPage, Page):
            raise ValueError('%s must be %s classtype' % (classType, Page))
        newPage.domain = self.environment.domain
        self.storeObj(pageName, newPage, classType)
        return newPage

    def storeEnvironment(self, envName: str, envObj: Environment):
        """
        Store a test environment
        @param envName: name to store
        @param envObj: <Environment> object to store
        @return: self
        """
        return self.storeObj(envName, envObj, Environment)

    def storeEngine(self, engineName: str, engineObj: WebDriver):
        """
        Store a WedDriver engine
        @param engineName: name to store
        @param engineObj: <WebDriver> object to store
        @return: self
        """
        return self.storeObj(engineName, engineObj, WebDriver)
