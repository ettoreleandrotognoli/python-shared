class Node(object):
    def call(self, resource, *args, **kwargs):
        raise NotImplementedError()

    def getattr(self, resource, attr):
        raise NotImplementedError()

    def setattr(self, resource, attr, value):
        raise NotImplementedError()

    def getitem(self, resource, key):
        raise NotImplementedError()

    def setitem(self, resource, key, value):
        raise NotImplementedError()
