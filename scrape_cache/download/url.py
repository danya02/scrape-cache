from .base import DownloadController
import requests

from ..database import CachedRequest 

class HttpController(DownloadController):
    """
    Download controller responsible for storing the response to a simple GET request to the provided URL.
    """

    def __init__(self, method='GET', **kwargs):
        """
        Keyword arguments provided here will be passed to the `requests.request` function.
        """
        self.method = method
        self.kwargs = kwargs

    def perform_get(self, url, raise_for_status=True, store_in_file=False):
        """
        Run the download, and create the database record representing it.

        If raise_for_status, this will raise an exception if the response code is not indicative of a successful request.
        """
        resp = requests.request(self.method, url, **self.kwargs)
        if raise_for_status:
            resp.raise_for_status()

        CachedRequest.new_from_response(resp, store_in_file=store_in_file)


    def __repr__(self):
        return f'HttpController(**{repr(self.kwargs)})'
