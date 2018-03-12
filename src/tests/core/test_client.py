from unittest import TestCase

from pyshared.client.rx import RemoteResourceManager
from pyshared.client.rx import TCPClient
from pyshared.serve import main as run_server
from pyshared.server.rx import TCPServer


class ClientTest(TestCase):
    server = None

    @classmethod
    def setUpClass(cls):
        cls.server = run_server(
            address='0.0.0.0',
            port=0,
            server_factory=TCPServer,
            initial_values={'a': 'test'},
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    def test_client(self):
        result = []
        client = RemoteResourceManager(
            lambda: TCPClient().connect('127.0.0.1', self.server.port)
        )
        client['a'].upper().subscribe(result.append)
        self.assertEqual(result, ['TEST'])
