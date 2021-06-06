from abc import ABC, abstractmethod

class DownloadController(ABC):
    """
    Class representing a method of fetching a specific resource.
    """

    @abstractmethod
    def __repr__(self) -> str:
        """
        Method returning a string representation of self.

        Because of the specifics of how this is used, this should evaluate to an instance equivalent to self.
        In particular, if any authentication data was provided when self was initialized, this data must be present in the return value of this.        

        >>> instance = Foo(bar='hello', baz='world')
        >>> repr(instance)
        "Foo(bar='hello', baz='world')"
        """
        raise NotImplementedError
