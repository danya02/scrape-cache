import peewee as pw
from playhouse.sqlite_ext import SqliteExtDatabase, JSONField
import datetime
import os
import uuid

dbase = SqliteExtDatabase('cache.db', pragmas=(
    ('cache_size', -1024 * 64),
    ('journal_mode', 'wal'),
    ('foreign_keys', 1)))


class MyModel(pw.Model):
    class Meta:
        database = dbase

def table(cls):
    dbase.create_tables([cls])
    return cls

@table
class Domain(MyModel):
    base_url = pw.CharField(help_text='https://example.com', unique=True)

@table
class CachedRequest(MyModel):
    method = pw.CharField(max_length=16, help_text='HTTP verb (GET, POST, ...)')
    domain = pw.ForeignKeyField(Domain)
    resource = pw.CharField(help_text='/hello/world.png?variant=5')
    request_body = pw.BlobField(null=True)
    request_headers = JSONField()

    access_time = pw.DateTimeField(default=datetime.datetime.now)

    response_headers = JSONField()
    response_body = pw.BlobField(help_text='If response_in_external_file, this contains a UTF-8 path to the file in the local filesystem')
    response_in_external_file = pw.BooleanField(default=False)

    @classmethod
    def new_from_response(cls, resp, store_in_file=False):
        inst = cls()
        req = resp.request
        inst.method = req.method
        base_url = req.url[:-len(req.path_url)]
        path_url = req.path_url
        inst.domain, _ = Domain.get_or_create(base_url=base_url)
        inst.resource = path_url

        body = req.body
        if body is None:
            inst.request_body = None
        else:
            if isinstance(body, str):
                body = bytes(body, 'utf-8')
            inst.request_body = body

        inst.request_headers = dict(req.headers)
        inst.response_headers = dict(resp.headers)
        if store_in_file:
            inst.response_in_external_file = True
            path = os.path.join(os.getcwd(), 'files', str(uuid.uuid4()))
            inst.response_body = bytes(path, 'utf-8')
            os.makedirs(os.path.join(os.getcwd(), 'files'), exist_ok=True)
            with open(path, 'wb') as handle:
                for chunk in resp.iter_content(chunk_size=16384):
                    handle.write(chunk)
        else:
            data = bytearray()
            for byte in resp.iter_content():
                data.extend(byte)
            inst.response_body = bytes(data)

        inst.save(force_insert=True)
        return inst

# from https://stackoverflow.com/a/29994957/5936187
class classproperty(object):
    def __init__(self, fget):
        self.fget = fget
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

@table
class ScheduledDownloadJob(MyModel):
    failed = pw.BooleanField(default=False, help_text='Should this job be ignored when considering jobs to execute? Has this job failed too many times and been given up on?', index=True)

    originally_scheduled_at = pw.DateTimeField(help_text='First time that the job was scheduled for, before any reschedules.')
    run_at = pw.DateTimeField(help_text='Next time to attempt executing this job, after any reschedules.', index=True)
    job_function = pw.CharField(help_text='_Function_ to run as part of executing this job. Not a function call.')
    backoff_controller = pw.CharField(default='ConstantBackoffController(seconds=5)', help_text='If the job function errors, use this controller to determine the next time to schedule the job.')
    reschedules = pw.IntegerField(default=0, help_text='The job was rescheduled this many times.')
    max_reschedules = pw.IntegerField(default=20, help_text='How many times to reschedule the job before giving up.')

    @classproperty
    def executable_jobs(cls):
        return cls.select().where(ScheduledDownloadJob.failed == False).where(ScheduledDownloadJob.run_at <= datetime.datetime.now())

@table
class ResourceNamespace(MyModel):
    name = pw.CharField(unique=True, help_text='Unique namespace for the type of resource involved, preferably hierarchically arranged: com.example.forum.post')

@table
class Resource(MyModel):
    namespace = pw.ForeignKeyField(ResourceNamespace)
    res_id = pw.CharField(help_text='Unique serverside resource identifier')
    fetched_at = pw.DateTimeField(default=datetime.datetime.now)
    content = pw.BlobField()
    content_in_external_file = pw.BooleanField(default=False)

    class Meta:
        primary_key = pw.CompositeKey('namespace', 'res_id')

    @classmethod
    def from_cached_request(cls, cached_req, namespace, res_id):
        existing = cls.get_or_none(namespace=namespace, res_id=res_id)
        if existing:
            existing.fetched_at = datetime.datetime.now()
            existing.content = cached_req.response_body
            existing.content_in_external_file = cached_req.response_in_external_file
            existing.save()
            return existing
        else:
            return cls.create(namespace=namespace, res_id=res_id, content=cached_req.response_body, content_in_external_file=cached_req.response_in_external_file)
