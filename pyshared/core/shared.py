import socket
from uuid import uuid4
from typing import Iterator
from typing import TypeVar
from typing import Type


def make_client_id(hostname=None, glue=':') -> str:
    hostname = hostname or socket.gethostname()
    return glue.join([hostname, uuid4().hex()])


def make_resource_name(obj, glue=':') -> str:
    return glue.join([obj.__class__.__name__, hex(id(obj)), uuid4().hex])


E = TypeVar('E')


class SharedResourcesManager(object):
    def get_nodes(self) -> Iterator:
        raise NotImplementedError()

    def get_resources(self) -> Iterator:
        raise NotImplementedError()

    def get_resource(self, resource_id, resource_class: Type[E] = None) -> E:
        raise NotImplementedError()

    def put_resource(self, resource_id, resource):
        raise NotImplementedError()


