import time
from queue import Queue
import threading
from rapidlyThreadPool import ThreadPoolExecutorShrinkAble


class ThreadPoolExecutorShrinkAbleWithSpecifyQueue(ThreadPoolExecutorShrinkAble):
    def __init__(self, *args, specify_work_queue=None, **kwargs):
        super(ThreadPoolExecutorShrinkAbleWithSpecifyQueue, self).__init__(*args, **kwargs)
        self.work_queue = specify_work_queue


class TpsThreadPoolExecutor(object):

    def __init__(self, tps=0, max_workers=500, specify_work_queue=None):
        """
        tps:   指定线程池每秒运行多少次函数，为0这不限制运行次数
        """
        self.tps = tps
        self.time_interval = 1 / tps if tps != 0 else 0
        self.pool = ThreadPoolExecutorShrinkAbleWithSpecifyQueue(max_workers=max_workers,
                                                                 specify_work_queue=specify_work_queue or Queue(
                                                                     max_workers))
        self._last_submit_task_time = time.time()
        self._lock_for_count_last_submit_task_time = threading.Lock()

    def submit(self, func, *args, **kwargs):
        with self._lock_for_count_last_submit_task_time:
            if self.time_interval:
                time.sleep(self.time_interval)
            return self.pool.submit(func, *args, **kwargs)

    def shutdown(self, wait=True):
        self.pool.shutdown(wait=wait)