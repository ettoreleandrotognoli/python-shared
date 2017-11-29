from threading import current_thread


def fdebug(func):
    func_name = func.__name__

    def wrapper(*args, **kwargs):
        prefix = 'DEBUG[{}]'.format(current_thread().getName())
        print(prefix, '\t>> {}'.format(func_name), args, kwargs)
        r = func(*args, **kwargs)
        print(prefix, '\t<< {}'.format(func_name), args, kwargs, '->', r)
        return r

    return wrapper


def mdebug(func):
    func_name = func.__name__

    def wrapper(self, *args, **kwargs):
        prefix = 'DEBUG[{}]'.format(current_thread().getName())
        print(prefix, '\t>> {}.{}'.format(self.__class__.__name__, func_name), args, kwargs)
        r = func(self, *args, **kwargs)
        print(prefix, '\t<< {}.{}'.format(self.__class__.__name__, func_name), args, kwargs, '->', r)
        return r

    return wrapper
