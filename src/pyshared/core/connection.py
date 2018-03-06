from abc import ABCMeta, abstractmethod
from typing import Dict
from typing import Iterator
from typing import Tuple
from typing import Type
from typing import TypeVar

from rx import Observer, Observable

E = TypeVar('E')


class SharedResourcesManager(object, metaclass=ABCMeta):
    @abstractmethod
    def get_resource(self, resource_id: str, resource_class: Type[E] = None) -> E:
        return NotImplemented


class DefaultSharedResourcesManager(SharedResourcesManager):
    def __init__(self, resources: Dict[str, object]):
        self.resources = resources

    def get_resource(self, resource_id: str, resource_class: Type[E] = None):
        resource = self.resources[resource_id]
        if resource_class is None:
            return resource
        return resource_class(resource)


class Command(object, metaclass=ABCMeta):
    @abstractmethod
    def exec(self, resource_manager: SharedResourcesManager):
        return NotImplemented


class CallCommand(Command):
    def __init__(self, resource_name: str, method: str, args: Iterator = [], kwargs: Dict = {}):
        self.resource_name = resource_name
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def exec(self, resource_manager: SharedResourcesManager):
        resource = resource_manager.get_resource(self.resource_name)
        return getattr(resource, self.method)(*self.args, **self.kwargs)


class CommandMapper(object, metaclass=ABCMeta):
    @abstractmethod
    def map(self, package) -> Command:
        return NotImplemented


class DictCommandMapper(CommandMapper):
    def __init__(self, commands_factory_map: Dict[str, callable]):
        self.commands_factory_map = commands_factory_map

    def map(self, package: Dict) -> Command:
        command_name = package['cmd']
        return self.commands_factory_map[command_name](**package.get('data', {}))

    def __call__(self, package: Dict) -> Command:
        return self.map(package)


default_command_mapper = DictCommandMapper({
    'call': CallCommand
})


class ReactiveSharedResourcesServer(object):
    def __init__(self, shared_manager: SharedResourcesManager):
        self.shared_manager = shared_manager

    def __call__(self, command: Command) -> Observable:
        result = command.exec(self.shared_manager)
        return Observable.just(result)

    def on_next(self, value: Tuple[Command, Observer]):
        command, response = value
        result = command.exec(self.shared_manager)
        response.on_next(result)
