import time


class Loop(object):
    """
    Supports methods to loop running function until expected condition is matched
    @author: Lex.Khuat
    @version: 1.1
    """

    @staticmethod
    def wait_until_true(timeout, frequency, wait_func, *args):
        """
        Loop running the expected expression until True is returned
        @param timeout: time to wait (seconds)
        @param frequency: interval of seconds each cycle run
        @param wait_func: function name to execute
        @param args: function args
        """
        maxtime = time.time() + int(timeout)
        while not wait_func(*args):
            if time.time() > maxtime:
                return False
            time.sleep(frequency)

    @staticmethod
    def wait_until_false(timeout, frequency, wait_func, *args):
        """
        Loop running the expected expression until False is returned
        @param timeout: time to wait (seconds)
        @param frequency: interval of seconds each cycle run
        @param wait_func: function name to execute
        @param args: function args
        """
        maxtime = time.time() + int(timeout)
        while wait_func(*args):
            if time.time() > maxtime:
                return True
            time.sleep(frequency)

    @staticmethod
    def wait_until_equal(timeout, frequency, expectation, wait_func, *args):
        """
        Loop running the expected expression until expectation value is matched
        @param timeout: time to wait (seconds)
        @param frequency: interval of seconds each cycle run
        @param expectation: the value to compare
        @param wait_func: function name to execute
        @param args: function args
        """
        maxtime = time.time() + int(timeout)
        while wait_func(*args) != expectation:
            if time.time() > maxtime:
                return False
            time.sleep(frequency)

    @staticmethod
    def wait_until_not_equal(timeout, frequency, expectation, wait_func, *args):
        """
        Loop running the expected expression until expectation value is not matched
        @param timeout: time to wait (seconds)
        @param frequency: interval of seconds each cycle run
        @param expectation: the value to compare
        @param wait_func: function name to execute
        @param args: function args
        """
        maxtime = time.time() + int(timeout)
        while wait_func(*args) == expectation:
            if time.time() > maxtime:
                return False
            time.sleep(frequency)
