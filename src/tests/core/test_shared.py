import json
import unittest

from pyshared.core.connection import CallCommand
from pyshared.core.connection import DefaultSharedResourcesManager
from pyshared.core.connection import ReactiveSharedResourcesServer
from pyshared.core.connection import default_command_mapper
from rx import Observable
from rx.subjects import Subject


class DefaultTest(unittest.TestCase):
    shared_resource = None

    def setUp(self):
        self.shared_resource = DefaultSharedResourcesManager({
            'number': 10
        })

    def test_call(self):
        call_command = CallCommand(
            resource_name='number',
            method='__add__',
            args=[7]
        )
        self.assertEqual(17, call_command.exec(self.shared_resource))


class ReactiveTest(unittest.TestCase):
    reactive_server = None

    def setUp(self):
        self.reactive_server = ReactiveSharedResourcesServer(DefaultSharedResourcesManager({
            'number': 10
        }))

    def test_call(self):
        call_command = CallCommand(
            resource_name='number',
            method='__sub__',
            args=[5]
        )
        subject = Subject()
        subject.subscribe(on_next=lambda e: self.assertEqual(5, e))
        self.reactive_server(call_command).subscribe(subject)

    def test_mapper(self):
        result = []
        Observable.from_([
            {'cmd': 'call', 'data': {'resource_name': 'number', 'method': '__sub__', 'args': [1]}},
            {'cmd': 'call', 'data': {'resource_name': 'number', 'method': '__add__', 'args': [5]}},
        ]).map(default_command_mapper) \
            .flat_map(self.reactive_server) \
            .subscribe(result.append)
        self.assertEqual(result, [9, 15])

    def test_json_mapper(self):
        result = []
        Observable.from_([
            '{"cmd": "call", "data": {"resource_name": "number", "method": "__sub__", "args": [1]}}',
            '{"cmd": "call", "data": {"resource_name": "number", "method": "__add__", "args": [5]}}',
        ]).map(json.loads) \
            .map(default_command_mapper) \
            .flat_map(self.reactive_server) \
            .subscribe(result.append)
        self.assertEqual(result, [9, 15])
