import time


class Timer:
    """
    A timer class to measure the time elapsed between start() and stop().
    """

    def __init__(self):
        self.start_time = None
        self.start_time = time.time()

    def elapsed_time(self, keep=2):
        """
        Return the elapsed time in seconds.
        """
        return round(time.time() - self.start_time, keep)
