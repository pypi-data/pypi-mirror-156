import os
import atexit
import queue
import sys
import threading
import time
import weakref
from loguru import logger
from concurrent.futures import Executor, Future

_shutdown = False
_threads_queues = weakref.WeakKeyDictionary()


def _python_exit():
    global _shutdown
    _shutdown = True
    items = list(_threads_queues.items())
    for t, q in items:
        q.put(None)
    for t, q in items:
        t.join()


atexit.register(_python_exit)


class _WorkItem(object):
    def __init__(self, future, fn, args, kwargs):
        self.future = future
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if not self.future.set_running_or_notify_cancel():
            return
        try:
            result = self.fn(*self.args, **self.kwargs)
        except BaseException as exc:
            logger.error(f'函数 {self.fn.__name__} 中发生错误，错误原因是 {type(exc)} {exc} ')
            self.future.set_exception(exc)
        else:
            self.future.set_result(result)

    def __str__(self):
        return f'{(self.fn.__name__, self.args, self.kwargs)}'


def set_thread_pool_executor_shrinkable(min_works, keep_alive_time):
    ThreadPoolExecutorShrinkAble.MIN_WORKERS = min_works
    ThreadPoolExecutorShrinkAble.KEEP_ALIVE_TIME = keep_alive_time


class ThreadPoolExecutorShrinkAble(Executor):
    MIN_WORKERS = 1
    KEEP_ALIVE_TIME = 10

    def __init__(self, max_workers: int = None, thread_name_prefix=''):
        self._max_workers = max_workers or 4
        self._thread_name_prefix = thread_name_prefix
        self.work_queue = self._work_queue = queue.Queue(max_workers or 10)
        self.jfThreads = weakref.WeakSet()
        self.lockComputeThreadsFreeCount = threading.Lock()
        self.threads_free_count = 0
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def changeThreadsFreeCount(self, change_num):
        with self.lockComputeThreadsFreeCount:
            self.threads_free_count += change_num

    def adjustThreadCount(self):
        if self.threads_free_count <= self.MIN_WORKERS and len(self.jfThreads) < self._max_workers:
            t = _CustomThread(self)
            t.daemon = True
            t.start()
            self.jfThreads.add(t)
            _threads_queues[t] = self._work_queue

    def submit(self, func, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('不能添加新的任务到线程池')
            f = Future()
            w = _WorkItem(f, func, args, kwargs)
            self.work_queue.put(w)
            self.adjustThreadCount()
            return f

    def shutdown(self, wait=True):  # noqa
        with self._shutdown_lock:
            self._shutdown = True
            self.work_queue.put(None)
        if wait:
            for t in self.jfThreads:
                t.join()


CustomThreadPoolExecutor = ThreadPoolExecutorShrinkAble


class _CustomThread(threading.Thread):
    _lock_for_judge_threads_free_count = threading.Lock()

    def __init__(self, executorBIG: ThreadPoolExecutorShrinkAble):
        super().__init__()
        self._ident = None
        self._executorSpeed = executorBIG

    def _remove_thread(self, stopCondition=''):
        logger.error(f'停止线程 {self._ident}, 触发条件是 {stopCondition} ')
        self._executorSpeed.changeThreadsFreeCount(-1)
        self._executorSpeed.jfThreads.remove(self)
        _threads_queues.pop(self)

    def run(self):
        self._executorSpeed.changeThreadsFreeCount(1)
        while True:
            try:
                work_item = self._executorSpeed.work_queue.get(block=True, timeout=self._executorSpeed.KEEP_ALIVE_TIME)
            except queue.Empty:
                with self._lock_for_judge_threads_free_count:
                    if self._executorSpeed.threads_free_count > self._executorSpeed.MIN_WORKERS:
                        self._remove_thread(
                            f'当前线程超过 {self._executorSpeed.KEEP_ALIVE_TIME} 秒没有任务，线程池中不在工作状态中的线程数量是 '
                            f'{self._executorSpeed.threads_free_count}，超过了指定的最小核心数量 {self._executorSpeed.MIN_WORKERS}')
                        break  # 退出while 1，即是结束。这里才是决定线程结束销毁，_remove_thread只是个名字而已，不是由那个来销毁线程。
                    else:
                        continue

            if work_item is not None:
                self._executorSpeed.changeThreadsFreeCount(-1)
                work_item.run()
                del work_item
                self._executorSpeed.changeThreadsFreeCount(1)
                continue
            if _shutdown or self._executorSpeed.shutdown:
                self._executorSpeed.work_queue.put(None)
                break


process_name_set = set()


def show_current_threads_num(sleep_time=600, process_name='', block=False, daemon=True):
    process_name = sys.argv[0] if process_name == '' else process_name

    def _show_current_threads_num():
        while True:
            logger.error(f'{process_name} {os.getpid()} 进程的线程数量是 -->{threading.active_count()}')
            time.sleep(sleep_time)

    if process_name not in process_name_set:
        if block:
            _show_current_threads_num()
        else:
            t = threading.Thread(target=_show_current_threads_num, daemon=daemon)
            t.start()
        process_name_set.add(process_name)


def get_current_threads_num():
    return threading.active_count()
