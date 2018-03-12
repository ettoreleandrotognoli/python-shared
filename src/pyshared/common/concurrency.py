import multiprocessing

from rx.concurrency import ThreadPoolScheduler


class Schedulers(object):
    computation = ThreadPoolScheduler(multiprocessing.cpu_count() * 2)
