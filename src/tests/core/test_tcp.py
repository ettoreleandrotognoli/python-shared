import unittest
from pyshared.core.tcp import TCPClient
from pyshared.core.tcp import TCPServer
from rx import Observer


class TCPTest(unittest.TestCase):
    def test_send_receive(self):
        test_case = self
        test_package = dict(a=1, b=2)

        client = TCPClient()

        class ObservableTest(Observer):
            def on_next(self, value):
                test_case.assertDictEqual(value, test_package)

            def on_completed(self):
                client.close()

            def on_error(self, error):
                pass

        server = TCPServer(ObservableTest())
        server.connect('0.0.0.0', 8000)
        server.start()

        client.connect('127.0.0.1', 8000)
        client.send(test_package)
        server.stop()
