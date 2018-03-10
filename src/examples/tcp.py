import json
import multiprocessing
import time

from rx.testing import marbles

m = marbles
from pyshared.core.ref import DefaultSharedResourcesManager
from pyshared.core.ref import ResourcesManagerListenerAdapter
from pyshared.core.ref import default_command_mapper
from pyshared.core.rx import ReactiveSharedResourcesServer
from pyshared.core.rx import TCPServer
from pyshared.core.rx import TCPServerConnection
from pyshared.core.utils import map_debug, fdebug
from rx import Observable
from rx.concurrency import ThreadPoolScheduler

address = '0.0.0.0'
optimal_thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


def safe(func, handler=lambda e: None):
    def wrapper(*args, **kwargs):
        try:
            return Observable.just(func(*args, **kwargs))
        except Exception as ex:
            handler(ex)
            return Observable.just(ex)

    return wrapper


def debug(name):
    def wrapper(*args, **kwargs):
        print(name, args, kwargs)

    return wrapper


def main():
    listener = ResourcesManagerListenerAdapter(
        on_init=debug('init'),
        on_finish=debug('finish'),
        on_call_resource=debug('call'),
        on_del_resource=debug('del'),
        on_set_resource=debug('set'),
        on_error=debug('error')
    )
    manager = DefaultSharedResourcesManager({
        'number': 10,
        'Observable': Observable
    }, listeners=[listener])
    pyshared = ReactiveSharedResourcesServer(manager)

    @fdebug
    def process_client(client: TCPServerConnection):
        try:
            client.as_observable(pool_scheduler) \
                .map(map_debug) \
                .map(lambda e: e.decode('utf-8')) \
                .map(json.loads) \
                .map(default_command_mapper) \
                .flat_map(pyshared) \
                .map(json.dumps) \
                .map(lambda e: e.encode('utf-8')) \
                .map(map_debug) \
                .retry() \
                .subscribe(client)
        except Exception as ex:
            print(ex)

    server = TCPServer()
    server.connect(address, 0)
    print("running at %s:%d" % (address, server.port))
    server.as_observable(pool_scheduler) \
        .subscribe(process_client)
    return server, manager


if __name__ == '__main__':
    try:
        server, manager = main()
    except Exception as ex:
        print(ex)
        exit(-1)
    try:
        while True:
            print('...')
            time.sleep(1)
    except KeyboardInterrupt as ex:
        del manager
        server.stop()
