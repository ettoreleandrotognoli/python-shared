class Resource():
    pass


class WrappedResource(object):
    _resource = None
    _resource_class = None

    def __init__(self, resource, resource_class):
        self._resource = resource
        self._resource_class = resource_class

    @classmethod
    def __instancecheck__(cls, instance):
        pass
