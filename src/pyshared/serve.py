import argparse
import json
import multiprocessing
import time
from distutils.util import strtobool
from pydoc import locate
from typing import Dict
from typing import List
from typing import Tuple

from pyshared.server.ref import LocalSharedResourcesManager
from pyshared.server.ref import default_command_mapper
from pyshared.server.rx import ReactiveSharedResourcesServer
from pyshared.server.rx import TCPServer
from pyshared.common.utils import map_debug
from rx import Observable
from rx.concurrency import ThreadPoolScheduler


class BuffAndSplit(object):
    def __init__(self, delimiter=b'\r\n', initial=b''):
        self.delimiter = delimiter
        self.buffer = initial

    def __call__(self, e):
        self.buffer += e
        if self.delimiter not in self.buffer:
            return Observable.empty()
        packages = self.buffer.split(self.delimiter)
        self.buffer = packages[-1]
        return Observable.from_(packages[:-1])


def main(address: str, port: int,
         server_factory,
         keep_connection: bool,
         panic: bool,
         encoding: Tuple[callable, callable],
         package_parser: Tuple[callable, callable],
         delimiter: bytes,
         workers: int,
         initial_packages: List[str],
         initial_values: Dict[str, object]):
    encode_func, decode_func = encoding
    from_pack, to_pack = package_parser
    manager = LocalSharedResourcesManager({
        **dict((package, locate(package)) for package in initial_packages),
        **initial_values
    })
    shared_server = ReactiveSharedResourcesServer(manager)

    def accept_client(client):
        print('accept client', client)
        try:
            observable_packages = client.as_observable(pool_scheduler) \
                .map(map_debug) \
                .flat_map(BuffAndSplit(delimiter, b'')) \
                .map(map_debug)
            if not keep_connection:
                observable_packages = observable_packages.first()
            result = observable_packages \
                .safe_map(decode_func, print) \
                .map(map_debug) \
                .safe_map(from_pack, print) \
                .safe_map(default_command_mapper, print) \
                .flat_map(shared_server) \
                .safe_map(to_pack, print) \
                .safe_map(encode_func, print) \
                .safe_map(lambda e: e + delimiter, print) \
                .map(map_debug)

            if not panic:
                result = result.retry()
            result.subscribe(client)
        except Exception as ex:
            print(ex)

    pool_scheduler = ThreadPoolScheduler(workers)
    server = server_factory()
    server.connect(*(address, port,))
    print(address, server.port)
    server.as_observable(pool_scheduler) \
        .subscribe(accept_client)


def wait_exit():
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        return


parsers = {
    'json': (json.loads, json.dumps)
}


def parse_parser(name):
    return parsers[name]


def parse_encoding(name):
    return lambda e: e.encode(name), lambda e: e.decode(name)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serve PyShared')
    parser.add_argument('address', type=str, nargs='?', default='127.0.0.1')
    parser.add_argument('port', type=int, nargs='?', default=0)
    parser.add_argument(
        '--keep', dest='keep_connection',
        type=strtobool, nargs='?', default=True
    )
    parser.add_argument(
        '--delimiter',
        type=bytes,
        nargs='?',
        default=b'\r\n'
    )
    parser.add_argument(
        '--encoding',
        type=parse_encoding,
        nargs='?',
        default='utf-8'
    )
    parser.add_argument(
        '--workers',
        type=int,
        nargs='?',
        default=multiprocessing.cpu_count() * 2
    )
    parser.add_argument(
        '--parser', dest='package_parser',
        type=parse_parser,
        nargs='?',
        default='json',
    )
    parser.add_argument(
        '--panic',
        type=strtobool,
        nargs='?',
        default=False
    )
    parser.add_argument(
        '--initial-values', dest='initial_values',
        type=json.loads,
        nargs='+',
        default={}
    )
    parser.add_argument(
        '--initial-loads', dest='initial_packages',
        type=str,
        nargs='+',
        default=[]
    )
    args = parser.parse_args()
    print(vars(args))
    main(server_factory=TCPServer, **vars(args))
    wait_exit()
