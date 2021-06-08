from .backoff import backoff_controllers
from .download import *
from .database import ScheduledDownloadJob
import traceback
import datetime


def process_single_job(job):
    try:
        func = eval(job.job_function, globals(), download_methods)
    except:
        print('Error while getting job function, marking job as failed right away.')
        traceback.print_exc()
        job.failed = True
        job.save()
        return

    try:
        func()
        print('Running job OK, deleting job record')
        job.delete_instance()
    except Exception as e:
        traceback.print_exc()
        print('Error while executing job function, trying to reschedule job...')
        try:
            backoff_ctrl = eval(job.backoff_controller, globals(), backoff_controllers)
        except:
            print('Error while getting backoff controller, marking job as failed right away.')
            traceback.print_exc()
            job.failed = True
            job.save()
            return
        interval = backoff_ctrl.get_interval(job, e)
        job.reschedules += 1
        if job.reschedules >= job.max_reschedules:
            print('Job was rescheduled too many times, marking job as failed.')
            job.failed = True
            job.save()
            return
        job.run_at = datetime.datetime.now() + interval
        job.save()
        return

def process_scheduled_jobs():
    for job in ScheduledDownloadJob.executable_jobs:
        process_single_job(job)
