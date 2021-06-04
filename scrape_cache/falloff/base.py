from abc import ABC, abstractmethod

class FalloffController(ABC):
    """
    Class that represents a falloff function.
    This is used to determine the time to wait until a task is rescheduled.
    """

    @abstractmethod
    def get_interval(self, job, error):
        """
        Calculate the interval to wait after this job failed.

        job is the database record of the job, in the state that it had
        before it ran and errored out.

        error is the exception that was raised by the job.

        Returns a datetime.timedelta.
        """

        raise NotImplementedError
