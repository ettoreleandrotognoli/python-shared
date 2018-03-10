import json
import unittest

from pyshared.core.ref import CallCommand
from pyshared.core.ref import LocalSharedResourcesManager
from pyshared.core.ref import DelCommand
from pyshared.core.ref import ListCommand
from pyshared.core.ref import SetCommand
from pyshared.core.ref import default_command_mapper
from pyshared.core.rx import ReactiveSharedResourcesServer
from rx import Observable


class DefaultTest(unittest.TestCase):
    shared_resource = None

    def setUp(self):
        self.shared_resource = LocalSharedResourcesManager({
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
        self.reactive_server = ReactiveSharedResourcesServer(LocalSharedResourcesManager({
            'number': 10
        }))

    def test_call(self):
        call_command = CallCommand(
            resource_name='number',
            method='__sub__',
            args=[5]
        )
        result = []
        self.reactive_server(call_command).subscribe(result.append)
        self.assertEqual(result, [5])

    def test_call_with_result(self):
        call_command = CallCommand(
            resource_name='number',
            method='__add__',
            args=[5],
            result='result'
        )
        result = []
        self.reactive_server(call_command).subscribe(result.append)
        self.assertEqual(result, [{'result': 15}])

    def test_call_any_result(self):
        call_command = CallCommand(
            resource_name='number',
            method='__add__',
            args=[5],
            result=True
        )
        result = []
        self.reactive_server(call_command).subscribe(result.append)
        self.assertEqual(15, list(result[0].values())[0])

    def test_list(self):
        list_command = ListCommand()
        result = []
        self.reactive_server(list_command).subscribe(result.append)
        self.assertEqual(result, [['number']])

    def test_set(self):
        set_command = SetCommand(
            resource_name='a',
            value=10
        )
        result = []
        self.reactive_server(set_command).subscribe(result.append)
        self.assertEqual(result, [{'a': 10}])

    def test_del(self):
        del_command = DelCommand(resource_name='number')
        result = []
        self.reactive_server(del_command).subscribe(result.append)
        self.assertEqual(result, ['number'])

    def test_mapper(self):
        result = []
        Observable.from_([
            {'cmd': 'call', 'resource_name': 'number', 'method': '__sub__', 'args': [1]},
            {'cmd': 'call', 'resource_name': 'number', 'method': '__add__', 'args': [5]},
        ]).map(default_command_mapper) \
            .flat_map(self.reactive_server) \
            .subscribe(result.append)
        self.assertEqual(result, [9, 15])

    def test_json_mapper(self):
        result = []
        Observable.from_([
            '{"cmd": "call", "resource_name": "number", "method": "__sub__", "args": [1]}',
            '{"cmd": "call", "resource_name": "number", "method": "__add__", "args": [5]}',
        ]).map(json.loads) \
            .map(default_command_mapper) \
            .flat_map(self.reactive_server) \
            .subscribe(result.append)
        self.assertEqual(result, [9, 15])
