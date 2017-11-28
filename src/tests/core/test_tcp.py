import unittest

from pyshared.core.tcp import TCPClient
from pyshared.core.tcp import TCPServer
from rx import Observable


class TCPTest(unittest.TestCase):
    received_package = None

    def test_send_receive(self):
        test_case = self
        test_package = dict(a=1, b=2)
        client = TCPClient()

        server = TCPServer()
        server.subscribe(on_next=lambda e: print(e))
        server.connect('0.0.0.0', 8000)
        server.start()

        Observable.from_([{'a': 1}, {'b': 2}]).subscribe(on_next=lambda e: print(e))

        client.connect('127.0.0.1', 8000)
        client.start()
        Observable.from_([{'a': 1}, {'b': 2}]).subscribe(on_next=client.send)
        client.subscribe(on_next=lambda e: print(e))

        server.stop()
        test_case.assertDictEqual(self.received_package, test_package)
