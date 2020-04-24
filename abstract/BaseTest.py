import logging
import os
from datetime import datetime
from time import time, sleep


class Scenario(tuple):
    """
    Model of test scenario using in data driven test
    @author: lex.khuat
    """
    @staticmethod
    def parse(data, indirect=False):
        ids = []
        rows = []
        for scenario in data:
            ids.append(scenario.__name__)
            rows.append(list(scenario))
        return rows, indirect, ids

    @staticmethod
    def gen(summary: str, args: tuple):
        """
        Generate a data driven test scenario with param input
        @param summary: Test summary/title of the scenario
        @param args: <Tuple> params
        @return: <Tuple> newScenario
        """
        scenario = Scenario(args)
        setattr(scenario, '__name__', summary)
        return scenario


class TestLog:
    """
    Test base class provide all methods support test logging to files
    @author: lex.khuat
    """
    log = logging.getLogger(__name__)
    logPath = '.'

    def setLogPath(self, dirpath=None):
        """
        Set dir path to export log file
        @param dirpath: directory path to log file
        @return: self
        """
        if dirpath is not None:
            self.logPath = os.path.realpath(dirpath)
        if not self.log.handlers:
            file_path = '%s\\%s_%s.log' \
                        % (self.logPath, self.__class__.__name__, datetime.now().strftime("%Y%m%d_%H%M%S"))
            formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(formatter)
            self.log.addHandler(file_handler)
        return self

    def setLogLevel(self, level):
        """
        Set log level
        @param level: level of log
        @return: self
        """
        self.log.setLevel(level)
        return self


class BaseTest(object):
    """
    Base test class provide all methods support functionality test
    @author: lex.khuat
    """
    testResults = []

    @classmethod
    def add_testResult(cls, scenario, actual, expect):
        """
        Store test result for later check
        @param scenario: description of the test scenario
        @param actual: actual value
        @param expect: expect value
        """
        cls.testResults.append({'Scenario': str(scenario),
                                 'Actual': actual,
                                 'Expect': expect})

    @staticmethod
    def sleep(seconds):
        """
        Sleep for amount of seconds before next action
        @param seconds: seconds to sleep
        """
        sleep(seconds)

class BaseUITest(BaseTest):
    """
    Base test class provide all methods support UI test
    @author: lex.khuat
    """


class BaseDBTest(BaseTest):
    """
    Base test class provide all methods support database test
    @author: lex.khuat
    """


class BaseUIPerformanceTest(BaseUITest):
    """
    Base test class provide all methods support UI performance test
    @author: lex.khuat
    """

    checkPoints = [{'name': 'start', 'laptime': time()}]

    def index(self, checkpoint):
        """
        Find index of the checkpoint
        @param checkpoint: checkpoint name
        @return: int as index of the checkpoint
        """
        for i, v in enumerate(self.checkPoints):
            if v['name'] == checkpoint:
                return i
        return None

    def reset(self):
        """
        Reset test time counter
        @return: self
        """
        self.checkPoints = [{'name': 'start', 'laptime': time()}]
        return self

    def lap(self, checkpoint=None):
        """
        Record the eplapsed time from the last record
        @param checkpoint: name of the checkpoint to record
        @return: self
        """
        if checkpoint in [i['name'] for i in self.checkPoints]:
            raise Exception('Checkpoint name already exists')
        if checkpoint is None:
            checkpoint = str(len(self.checkPoints))
        self.checkPoints.append({'name': str(checkpoint), 'laptime': time()})
        return self

    def eplapse(self, check=None, lastcheck=None):
        """
        Get the duration between 2 checkpoint
        @param check: to checkpoint (last checkpoint if none)
        @param lastcheck: from checkpoint (to checkpoint - 1) if none
        @return: duration
        """
        check = self.checkPoints[-1] if check is None \
            else self.checkPoints[self.index(check)]
        lastcheck = self.checkPoints[self.index(check['name']) - 1] if lastcheck is None \
            else self.checkPoints[self.index(lastcheck)]
        duration = check['laptime'] - lastcheck['laptime']
        self.log.info(check['name'] + ' in {:0.2f} seconds'.format(duration))
        return duration

    eplapse = property(eplapse)
