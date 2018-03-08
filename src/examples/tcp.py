import json
import multiprocessing
import time

from pyshared.core.connection import DefaultSharedResourcesManager
from pyshared.core.connection import ReactiveSharedResourcesServer
from pyshared.core.connection import ResourcesManagerListenerAdapter
from pyshared.core.connection import default_command_mapper
from pyshared.core.tcp import TCPServer
from pyshared.core.tcp import TCPServerConnection
from pyshared.core.utils import map_debug, fdebug
from rx import Observable
from rx.concurrency import ThreadPoolScheduler

address = '0.0.0.0'
port = 8001
optimal_thread_count = multiprocessing.cpu_count() + 1
pool_scheduler = ThreadPoolScheduler(optimal_thread_count)


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
        on_set_resource=debug('set')
    )
    manager = DefaultSharedResourcesManager({
        'number': 10,
    }, listeners=[listener])
    pyshared = ReactiveSharedResourcesServer(manager)

    @fdebug
    def process_client(client: TCPServerConnection):
        Observable.from_(client.as_iterable(), pool_scheduler) \
            .map(map_debug) \
            .map(lambda e: e.decode('utf-8')) \
            .map(json.loads) \
            .map(default_command_mapper) \
            .map(map_debug) \
            .flat_map(pyshared) \
            .map(map_debug) \
            .map(json.dumps) \
            .map(lambda e: e.encode('utf-8')) \
            .map(map_debug) \
            .subscribe(client)

    server = TCPServer()
    Observable.from_(server.connect_as_iterable(address, port), pool_scheduler) \
        .subscribe(process_client)


if __name__ == '__main__':
    try:
        main()
        while True:
            print('...')
            time.sleep(1)
    except Exception as ex:
        print(ex)
