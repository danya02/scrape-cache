import peewee as pw
import datetime

dbase = pw.SqliteDatabase('cache.db')

class MyModel(pw.Model):
    class Meta:
        database = dbase

def table(cls):
    dbase.create_tables([cls])
    return cls

@table
class Domain(MyModel):
    base_url = pw.CharField(help_text='https://example.com')

@table
class CachedRequest(MyModel):
    method = pw.CharField(max_length=16, help_text='HTTP verb (GET, POST, ...)')
    domain = pw.ForeignKeyField(Domain)
    resource = pw.CharField(help_text='/hello/world.png?variant=5')
    request_body = pw.BlobField()
    request_headers = pw.JSONField()

    access_time = pw.DateTimeField(default=datetime.datetime.now)

    response_headers = pw.JSONField()
    response_body = pw.BlobField(help_text='If response_in_external_file, this contains a UTF-8 path to the file in the local filesystem')
    response_in_external_file = pw.BooleanField(default=False)

@table
class ScheduledDownloadJob(MyModel):
    failed = pw.BooleanField(default=False, help_text='Should this job be ignored when considering jobs to execute? Has this job failed too many times and been given up on?', index=True)

    originally_scheduled_at = pw.DateTimeField(help_text='First time that the job was scheduled for, before any reschedules.')
    run_at = pw.DateTimeField(help_text='Next time to attempt executing this job, after any reschedules.', index=True)
    job_function = pw.CharField(help_text='_Function_ to run as part of executing this job. Not a function call.')
    backoff_controller = pw.CharField(default='ConstantBackoffController(seconds=5)', help_text='If the job function errors, use this controller to determine the next time to schedule the job.')
    reschedules = pw.IntegerField(default=0, help_text='The job was rescheduled this many times.')
    max_reschedules = pw.IntegerField(default=20, help_text='How many times to reschedule the job before giving up.')

    @property
    @staticmethod
    def executable_jobs():
        return ScheduledDownloadJob.select().where(ScheduledDownloadJob.failed == False).where(ScheduledDownloadJob.run_at <= datetime.datetime.now())

