from .base import FalloffController
import datetime

class ConstantFalloffController(FalloffController):
    """
    Falloff controller with a constant delay.
    The delay is provided at initialization, by default it is 5 seconds.
    """

    def __init__(self, days=0, seconds=5, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        self.delay = datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds, milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    def get_interval(self, job, error):
        return self.delay 
