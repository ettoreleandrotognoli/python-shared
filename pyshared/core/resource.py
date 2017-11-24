from pyshared.core.node import Node


class Resource(object):
    def __init__(self, resource_id, node: Node):
        self._resource_id = resource_id
        self._node = node

    def __getattr__(self, item):
        return self._node.getattr(self._resource_id, item)

    def __setattr__(self, key, value):
        return self._node.setattr(self._resource_id, key, value)

    def __getitem__(self, key):
        return self._node.getitem(self._resource_id, key)

    def __setitem__(self, key, value):
        return self._node.setitem(self._resource_id, key, value)

    def __call__(self, *args, **kwargs):
        return self._node.call(self._resource_id, *args, **kwargs)


class WrappedResource(object):
    _resource = None
    _resource_class = None

    def __init__(self, resource, resource_class):
        self._resource = resource
        self._resource_class = resource_class

    @classmethod
    def __instancecheck__(cls, instance):
        pass
