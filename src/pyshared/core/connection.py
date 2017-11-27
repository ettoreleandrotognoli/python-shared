from rx import Observer


class Protocol(Observer):
    commands = {
        'call': 'call_resource',
        'list': 'list_resources',
    }

    def on_next(self, value):
        method_name = value[0]
        params = value[1:]
        getattr(self, method_name)(*params)

    def list_resources(self):
        raise NotImplementedError()

    def call_resource(self, resource_id, args, kwargs, callback):
        raise NotImplementedError()
