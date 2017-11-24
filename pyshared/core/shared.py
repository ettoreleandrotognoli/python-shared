from uuid import uuid4
from typing import Iterator
from typing import TypeVar
from typing import Type


def make_client_id() -> str:
    pass


def make_resource_name(obj, glue=':') -> str:
    return glue.join([obj.__class__.__name__, hex(id(obj)), uuid4().hex])


E = TypeVar('E')


class SharedResourcesManager(object):
    def list_nodes(self) -> Iterator:
        raise NotImplementedError()

    def list_resources(self) -> Iterator:
        raise NotImplementedError()

    def get_resource(self, resource_id, resource_class: Type[E] = None) -> E:
        raise NotImplementedError()

    def put_resource(self, resource_id, resource):
        raise NotImplementedError()


class LocalResourcesManager(SharedResourcesManager):
    resources = None

    def __init__(self, resources=None):
        self.resources = resources or dict()

    def call(self, resource, method, *args, **kwargs):
        return getattr(self.resources[resource], method)(*args, **kwargs)

    def getattr(self, resource, attr):
        return getattr(self.resources[resource], attr)

    def setattr(self, resource, attr, value):
        return setattr(self.resources[resource], attr, value)

    def find_instances_of(self, types):
        return [name for name, value in self.resources.items() if isinstance(value, types)]

    def register(self, obj, name=None, type=None):
        type = type or obj.__class__
        name = name or make_resource_name(obj)
