import socket
from functools import partial
from typing import Iterator
from typing import Type
from typing import TypeVar
from uuid import uuid4

from rx import Observer


def make_client_id(hostname=None, glue=':') -> str:
    hostname = hostname or socket.gethostname()
    return glue.join([hostname, uuid4().hex()])


def make_resource_name(obj, glue=':') -> str:
    return glue.join([obj.__class__.__name__, hex(id(obj)), uuid4().hex])


class RemoteNode(object):
    def __init__(self, manager: 'RemoteResourcesManager', resource_id):
        self._manager = manager
        self._resource_id = resource_id

    def __getattr__(self, item):
        return partial(self._manager.call, self._resource_id, item)


class RemoteResourcesManager(SharedResourcesManager):
    def __init__(self, address: str, port: int):
        pass

    def call(self, resource_id, method, *args, **kwargs):
        pass

    def get_nodes(self) -> Iterator:
        pass

    def get_resources(self):
        pass

    def get_resource(self, resource_id, resource_class: Type[E] = None) -> E:
        pass


class LocalResourcesManager(SharedResourcesManager):
    resources = None

    def __init__(self, resources=None):
        self.resources = resources or dict()

    def call(self, resource, method, *args, **kwargs):
        return getattr(self.resources[resource], method)(*args, **kwargs)

    def get_resource(self, resource_id, resource_class: Type[E] = None) -> E:
        return self.resources[resource_id]

    def put_resource(self, resource, resource_id=None):
        resource_id = resource_id or make_resource_name(resource)
        self.resources[resource_id] = resource


class ResourceServer(Observer):
    def __init__(self, resource_map: dict):
        self.resource_map = resource_map

    def on_completed(self):
        pass

    def on_error(self, error):
        pass

    def on_next(self, value):
        resource_id, args, kwargs, callback = value
        if isinstance(resource_id, str):
            resource_id = [resource_id]
        resource = self.resource_map.get(resource_id[0], None)
        if not resource:
            raise Exception()
        action = resource
        for key in resource_id[1:]:
            action = getattr(action, key)
        if not action:
            raise Exception()
        callback(action(*args, **kwargs))
