from typing import Type
from pyshared.core.shared import SharedResourcesManager
from pyshared.core.shared import E
from paho.mqtt import client as mqtt


class MQTTSharedResources(SharedResourcesManager):
    nodes = None
    resources = None
    mqtt_client = None

    def __init__(self):
        self.mqtt_client = mqtt.Client()

    def get_nodes(self):
        pass

    def get_resources(self):
        pass

    def get_resource(self, resource_id, resource_class: Type[E] = None):
        pass

    def put_resource(self, resource_id, resource):
        pass
