from typing import Dict
from typing import Iterator
from typing import List
from uuid import uuid4

from pyshared.core.api import *

NOOP = lambda *args, **kwargs: None


class ResourcesManagerListenerAdapter(ResourcesManagerListener):
    on_init = NOOP
    on_finish = NOOP
    on_set_resource = NOOP
    on_call_resource = NOOP
    on_del_resource = NOOP
    on_error = NOOP

    def __init__(self, on_init=NOOP,
                 on_finish=NOOP,
                 on_set_resource=NOOP,
                 on_call_resource=NOOP,
                 on_del_resource=NOOP,
                 on_error=NOOP):
        self.on_init = on_init
        self.on_finish = on_finish
        self.on_set_resource = on_set_resource
        self.on_call_resource = on_call_resource
        self.on_del_resource = on_del_resource
        self.on_error = on_error


class BaseSharedResourcesManager(SharedResourcesManager, metaclass=ABCMeta):
    def __init__(self, listeners: List[ResourcesManagerListener] = None):
        self.listeners = listeners or []

    def add_listener(self, listener: ResourcesManagerListener):
        self.listeners.append(listener)

    def remove_listener(self, listener: ResourcesManagerListener):
        self.listeners.remove(listener)

    def fire_on_init(self, *args, **kwargs):
        for listener in self.listeners:
            try:
                listener.on_init(*args, source=self, **kwargs)
            except Exception as ex:
                listener.on_error(ex)

    def fire_on_finish(self, *args, **kwargs):
        for listener in self.listeners:
            try:
                listener.on_finish(*args, source=self, **kwargs)
            except Exception as ex:
                listener.on_error(ex)

    def fire_on_set_resource(self, *args, **kwargs):
        for listener in self.listeners:
            try:
                listener.on_set_resource(*args, source=self, **kwargs)
            except Exception as ex:
                listener.on_error(ex)

    def fire_on_del_resource(self, *args, **kwargs):
        for listener in self.listeners:
            try:
                listener.on_del_resource(*args, source=self, **kwargs)
            except Exception as ex:
                listener.on_error(ex)

    def fire_on_call_resource(self, *args, **kwargs):
        for listener in self.listeners:
            try:
                listener.on_call_resource(*args, source=self, **kwargs)
            except Exception as ex:
                listener.on_error(ex)


class ResourceAdapter(object):
    def __init__(self, manager, key, resource, parent_adapter: 'ResourceAdapter' = None):
        self._parent_adapter = parent_adapter
        self._key = key
        self._manager = manager
        self._resource = resource

    def __call__(self, *args, **kwargs):
        result = self._resource(*args, **kwargs)
        self._manager.fire_on_call_resource(
            resource=self._resource,
            key=self._key,
            result=result,
            args=args,
            kwargs=kwargs
        )
        return result

    def __getattr__(self, attr_name):
        attr_value = getattr(self._resource, attr_name)
        return ResourceAdapter(key=self._key, parent_adapter=self, manager=self._manager, resource=attr_value)


class LocalSharedResourcesManager(BaseSharedResourcesManager):
    def __init__(self, resources: Dict[str, object], listeners: List[ResourcesManagerListener] = None):
        super().__init__(listeners=listeners)
        self.resources = resources
        self.fire_on_init(resources=self.resources)

    def __del__(self):
        self.fire_on_finish()
        super().__del__()

    def __setitem__(self, key: str, value: object):
        old_value = self.resources.get(key, None)
        self.resources[key] = value
        self.fire_on_set_resource(key=key, value=value, old_value=old_value)

    def __delitem__(self, key):
        del self.resources[key]
        self.fire_on_del_resource(key=key)

    def __getitem__(self, key: str):
        resource = self.resources.get(key, None)
        if resource is None:
            return None
        return ResourceAdapter(self, key, resource)

    def __len__(self):
        return len(self.resources)

    def __iter__(self):
        return (k for k in self.resources.keys())


class CallCommand(Command):
    def __init__(self, resource_name: str, method: str, result=False, args: Iterator = [], kwargs: Dict = {}):
        self.resource_name = resource_name
        self.method = method
        self.args = args
        self.kwargs = kwargs
        self.result = result

    def exec(self, resource_manager: SharedResourcesManager):
        resource = resource_manager[self.resource_name]
        result = getattr(resource, self.method)(*self.args, **self.kwargs)
        if not self.result:
            return result
        resource_name = self.result if self.result is not True else str(uuid4())
        resource_manager[resource_name] = result
        return {resource_name: result}


class UnknownCommand(Command):
    def __init__(self, *args, **kwargs):
        pass

    def exec(self, resource_manager: SharedResourcesManager):
        return {'error': 'command  not found'}


class ExceptionCommand(Command):
    def __init__(self, exception: Exception):
        self.exception = exception

    def exec(self, resource_manager: SharedResourcesManager):
        return {'error': str(self.exception)}


class SetCommand(Command):
    def __init__(self, resource_name: str = None, value: object = None):
        self.resource_name = resource_name
        self.value = value

    def exec(self, resource_manager: SharedResourcesManager):
        resource_name = self.resource_name if self.resource_name else str(uuid4())
        resource_manager[resource_name] = self.value
        return {resource_name: self.value}


class DelCommand(Command):
    def __init__(self, resource_name: str):
        self.resource_name = resource_name

    def exec(self, resource_manager: SharedResourcesManager):
        del resource_manager[self.resource_name]
        return self.resource_name


class ListCommand(Command):
    def __init__(self, filter=None):
        self.filter = filter

    def exec(self, resource_manager: SharedResourcesManager):
        return list(filter(self.filter, resource_manager))


class DictCommandMapper(CommandMapper):
    UNKNOWN_COMMAND = UnknownCommand

    def __init__(self, commands_factory_map: Dict[str, callable]):
        self.commands_factory_map = commands_factory_map

    def map(self, package: Dict) -> Command:
        command_name = package.pop('cmd', None)
        try:
            return self.commands_factory_map.get(command_name, self.UNKNOWN_COMMAND)(**package)
        except Exception as ex:
            return ExceptionCommand(ex)

    def __call__(self, package: Dict) -> Command:
        return self.map(package)


default_command_mapper = DictCommandMapper({
    'call': CallCommand,
    'set': SetCommand,
    'del': DelCommand,
    'list': ListCommand
})
