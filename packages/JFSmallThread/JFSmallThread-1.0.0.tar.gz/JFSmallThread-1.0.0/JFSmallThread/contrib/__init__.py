import abc
import queue
import threading
import time
from queue import LifoQueue
from loguru import logger


class ObjectPool(object):
    def __init__(self, object_type, object_init_kwargs: dict = None, object_pool_size=10, max_idle_seconds=30 * 60):
        """
        :param object_type: 对象类型，将会实例化此类
        :param object_init_kwargs: 对象的__init__方法的初始化参数
        :param object_pool_size: 对象池大小
        :param max_idle_seconds: 最大空闲时间，大于次时间没被使用的对象，将会被自动摧毁和弹出。摧毁是自动调用对象的clean_up方法
        """
        self._object_init_kwargs = {} if object_init_kwargs is None else object_init_kwargs
        self._max_idle_seconds = max_idle_seconds  # 大于此空闲时间没被使用的对象，将会被自动摧毁从对象池弹出。
        self.object_pool_size = object_pool_size
        self.queue = self._queue = LifoQueue(object_pool_size)
        self._lock = threading.Lock()
        self.is_using_num = 0
        self._has_create_object_num = 0
        self.object_type = object_type
        self.checkAndCleanupObjects()

    def checkAndCleanupObjects(self):
        with self._lock:
            t0 = time.time()
            to_be_requeue_object = []
            while 1:
                try:
                    obj = self._queue.get_nowait()
                except queue.Empty:
                    break
                else:
                    if time.time() - obj.the_obj_last_use_time > self._max_idle_seconds:
                        threading.Thread(target=obj.clean_up).start()
                        logger.info(f'此对象空闲时间超过 {self._max_idle_seconds}  秒，使用 {obj.clean_up} 方法 自动摧毁{obj}')
                        self._has_create_object_num -= 1
                    else:
                        to_be_requeue_object.append(obj)
            [self._queue.put_nowait(obj) for obj in to_be_requeue_object]
            if time.time() - t0 > 5:
                logger.info(f'耗时 {time.time() - t0}')

    def borrowOneObject(self, block, timeout):
        with self._lock:
            try:
                if self._queue.qsize() == 0 and self._has_create_object_num < self.object_pool_size:
                    obj = self.object_type(**self._object_init_kwargs)
                    self._queue.put(obj)
                    self._has_create_object_num += 1
                obj = self._queue.get(block, timeout)
                self.is_using_num += 1
                obj.the_obj_last_use_time = time.time()
                return obj
            except queue.Empty as e:
                logger.info(f'{e}  对象池暂时没有可用的对象了，请把timeout加大、或者不设置timeout(没有对象就进行永久阻塞等待)、或者设置把对象池的数量加大')
                raise e
            except Exception as e:
                logger.info(e)
                raise e
            finally:
                pass

    def _back_a_object(self, obj):
        if getattr(obj, 'is_available', None) is False:
            logger.info(f'{obj} 不可用,不放入')
            self._has_create_object_num -= 1
        else:
            self._queue.put(obj)
        self.is_using_num -= 1

    def get(self, block=True, timeout=None):
        return _ObjectContext(self, block=block, timeout=timeout)


class _ObjectContext(object):
    def __init__(self, pool: ObjectPool, block, timeout):
        self.jf_pool = pool
        self._block = block
        self._timeout = timeout
        self.obj = None

    def __enter__(self):
        self.obj = self.jf_pool.borrowOneObject(self._block, self._timeout)
        self.obj.is_available = True
        self.obj.before_use()
        return self.obj

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type in getattr(self.obj, 'error_type_list_set_not_available', []):
            self.obj.setNotAvailable()
        if self.obj is not None:
            self.obj.before_back_to_queue(exc_type, exc_val, exc_tb)
            self.jf_pool.borrowOneObject(self.obj, self._timeout)
        self.obj = None

    def __del__(self):
        if self.obj is not None:
            self.jf_pool.borrowOneObject(self.obj, self._timeout)
        self.obj = None


class AbstractObject(metaclass=abc.ABCMeta, ):
    error_type_list_set_not_available = []  # 可以设置当发生了什么类型的错误，就把对象设置为失效不可用。

    @abc.abstractmethod
    def __init__(self):
        self.is_available = False
        self.core_obj = None  # 这个主要是为了把自定义对象的属性指向的核心对象的方法自动全部注册到自定义对象的方法。

    @abc.abstractmethod
    def clean_up(self):
        """ 这里写关闭操作，如果没有逻辑，可以写 pass """

    def before_use(self):
        """ 可以每次对取出来的对象做一些操作"""
        pass

    def setNotAvailable(self):
        pass

    @abc.abstractmethod
    def before_back_to_queue(self, exc_type, exc_val, exc_tb):
        """ 这里写 with语法退出__exit__前的操作，如果没有逻辑，可以写 pass """

    def __getattr__(self, item):
        if 'core_obj' in self.__dict__:
            return getattr(self.core_obj, item)
        raise ValueError(f'{item} 方法或属性不存在')
