'''cping.protocols.tcp tests'''
import socket
import time
import unittest

import cping.protocols.tcp
import cping.protocols.tests


class TestPing(unittest.TestCase):
    '''cping.protocols.tcp.Ping tests.'''

    def test_change_interval(self):
        '''Change the interval in the middle of the test.'''
        protocol = cping.protocols.tcp.Ping(50000)
        cping.protocols.tests.ping_change_interval(self, protocol)

    def test_change_port(self):
        '''Change the port in the middle of the test. The first port is open,
        the second one is closed (TCP-RST).'''
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 50000))
        server.listen()

        host = cping.protocols.tcp.Ping(50000, 0.5)('127.0.0.1')
        host.start()

        # Wait for the first attempt to be dispatched then change the port
        time.sleep(0.25)
        host.protocol.port = 50001

        # Wait for the remainder of the first attempt + half of the second attempt
        time.sleep(0.5)
        host.stop(block=True)
        server.close()

        self.assertEqual(len(host.results), 2)

        # TCP-SYN
        self.assertNotEqual(host.results[0]['latency'], -1)
        self.assertFalse(host.results[0]['error'])

        # TCP-RST
        self.assertNotEqual(host.results[1]['latency'], -1)
        self.assertTrue(host.results[1]['error'])

    def test_failed_resolution(self):
        '''Failed resolution.'''
        cping.protocols.tests.resolve_failed(self, cping.protocols.tcp.Ping(1))

    def test_host_closed(self):
        '''TCP-RST is sent back.'''
        host = cping.protocols.tcp.Ping(50001)('127.0.0.1')
        cping.protocols.tests.ping_loop_once(host)

        self.assertEqual(len(host.results), 1)
        self.assertNotEqual(host.results[0]['latency'], -1)
        self.assertTrue(host.results[0]['error'])

    def test_host_not_responding(self):
        '''Nothing is sent back.'''
        host = cping.protocols.tcp.Ping(50002, 0.2)('1.2.3.4')
        cping.protocols.tests.ping_loop_once(host)

        self.assertEqual(len(host.results), 1)
        self.assertEqual(host.results[0]['latency'], -1)
        self.assertFalse(host.results[0]['error'])

    def test_host_open(self):
        '''A successful TCP handshake.'''
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('127.0.0.1', 50003))
        server.listen()

        host = cping.protocols.tcp.Ping(50003)('127.0.0.1')
        cping.protocols.tests.ping_loop_once(host)
        server.close()

        self.assertEqual(len(host.results), 1)
        self.assertNotEqual(host.results[0]['latency'], -1)
        self.assertFalse(host.results[0]['error'])

    def test_invalid_type_port(self):
        '''TCP with an invalid port type.'''
        with self.assertRaisesRegex(TypeError, 'port must be an integer'):
            cping.protocols.tcp.Ping('h')

    def test_invalid_value_port(self):
        '''TCP with an invalid port value.'''
        regex = 'port outside of range 1-65535'

        with self.assertRaisesRegex(ValueError, regex):
            cping.protocols.tcp.Ping(0)

        with self.assertRaisesRegex(ValueError, regex):
            cping.protocols.tcp.Ping(65536)
