import multiprocessing.pool
import logging


def run(jobs):
    pool = multiprocessing.pool.ThreadPool(processes=len(jobs))
    try:
        futures = []
        for job in jobs:
            kwargs = dict(job)
            args = ()
            del kwargs['callback']
            if 'args' in job:
                args = job['args']
                del kwargs['args']
            futures.append(pool.apply_async(_safeRun, args=(job['callback'], args, kwargs)))
        for future in futures:
            future.wait(timeout=2 ** 31)
        for future in futures:
            future.get()
    finally:
        pool.close()


def _safeRun(callback, args, kwargs):
    try:
        callback(*args, **kwargs)
    except:
        logging.exception("Running %(callback)s on '%(args)s'/'%(kwargs)s'", dict(
            callback=callback, args=args, kwargs=kwargs))
        raise
