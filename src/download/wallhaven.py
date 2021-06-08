from .base import DownloadController
import requests
from ..database import CachedRequest, ScheduledDownloadJob, ResourceNamespace, Resource
import random
import datetime
import json

class WallhavenController(DownloadController):
    """
    Class representing the API for https://wallhaven.cc/.
    """

    def __init__(self, api_key=None):
        """
        You can get your API key at: https://wallhaven.cc/settings/account
        """
        self.api_key = api_key

    def __repr__(self):
        return f'WallhavenController(api_key={repr(self.api_key)})'

    def schedule_download_listing(self, limit=100, **params):
        if self.api_key:
            params.update({'apikey': self.api_key})
        if limit:
            it = iter(range(limit))
        else:
            it = iter(int, 1)

        scheduled_time = datetime.datetime.now()
        ns, _ = ResourceNamespace.get_or_create(name='cc.wallhaven.wallpaper.data.brief')
        try:
            for page, _ in enumerate(iter(int, 1)):
                page += 1
                params.update({'page': page})
                req = requests.get('https://wallhaven.cc/api/v1/search', params=params)
                CachedRequest.new_from_response(req)
                data = req.json()

                for row in data['data']:
                    existing = Resource.get_or_none(namespace=ns, res_id=row['id'])
                    if existing:
                        existing.fetched_at = datetime.datetime.now()
                        existing.content = bytes(json.dumps(row), 'utf-8')
                        existing.save()
                    else:
                        Resource.create(namespace=ns, res_id=row['id'], content=bytes(json.dumps(row), 'utf-8'))

                for row in data['data']:
                    next(it)
                    url = row['path']
                    res_id = row['id']
                    image_ns, _ = ResourceNamespace.get_or_create(name='cc.wallhaven.wallpaper.image')
                    if Resource.get_or_none(namespace=image_ns, res_id=res_id):
                       continue
                    scheduled_time += datetime.timedelta(seconds=random.random()*5)
                    ScheduledDownloadJob.create(originally_scheduled_at=scheduled_time, run_at=scheduled_time, job_function=f'SimpleFileResourceController({url!r}, {image_ns.name!r}, {res_id!r}).fetch')

                if not data['data']:
                    raise StopIteration

        except StopIteration:
            return

