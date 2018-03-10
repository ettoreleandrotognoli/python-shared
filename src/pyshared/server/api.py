from abc import ABCMeta, abstractmethod


class ResourcesManagerListener(object, metaclass=ABCMeta):
    @abstractmethod
    def on_init(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def on_finish(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def on_set_resource(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def on_del_resource(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def on_call_resource(self, *args, **kwargs):
        return NotImplemented

    @abstractmethod
    def on_error(self, ex: Exception):
        return NotImplemented


class SharedResourcesManager(object, metaclass=ABCMeta):
    @abstractmethod
    def add_listener(self, listener: ResourcesManagerListener):
        return NotImplemented

    @abstractmethod
    def remove_listener(self, listener: ResourcesManagerListener):
        return NotImplemented

    @abstractmethod
    def __getitem__(self, item):
        return NotImplemented

    @abstractmethod
    def __setitem__(self, key, value):
        return NotImplemented

    @abstractmethod
    def __iter__(self):
        return NotImplemented

    @abstractmethod
    def __len__(self):
        return NotImplemented


class Command(object, metaclass=ABCMeta):
    @abstractmethod
    def exec(self, resource_manager: SharedResourcesManager):
        return NotImplemented


class CommandMapper(object, metaclass=ABCMeta):
    @abstractmethod
    def map(self, package) -> Command:
        return NotImplemented
