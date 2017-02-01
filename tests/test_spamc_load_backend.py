from __future__ import absolute_import
import os
import sys
import threading
try:
    import unittest2
except ImportError:
    if sys.version_info < (2, 7):
        raise
    import unittest as unittest2

from spamc import SpamC
from spamc import backend_eventlet
from spamc.exceptions import SpamCError

from ._s import return_tcp


class TestSpamCTCP(unittest2.TestCase):

    @classmethod
    def setUpClass(cls):
        gzip = False
        cls.using_sa = True
        if os.environ.get('SPAMD_HOST', None) is None:
            cls.tcp_server = return_tcp(10030)
            t1 = threading.Thread(target=cls.tcp_server.serve_forever)
            t1.setDaemon(True)
            t1.start()
            cls.using_sa = False
        if os.environ.get('SPAMD_COMPRESS', None) and \
                os.environ.get('CI', False) is False:
            gzip = True
        cls.spamc_tcp = SpamC(
            host=os.environ.get('SPAMD_HOST', '127.0.0.1'),
            port=int(os.environ.get('SPAMD_PORT', 10030)),
            gzip=gzip,
            compress_level=int(os.environ.get('SPAMD_COMPRESS_LEVEL', 6)),
            backend=backend_eventlet)
        path = os.path.dirname(os.path.dirname(__file__))
        cls.filename = os.path.join(path, 'examples', 'sample-spam.txt')

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'tcp_server'):
            cls.tcp_server.shutdown()

    def test_spamc_tcp_no_conn(self):
        spamc_tcp = SpamC(host='127.0.0.1', port=10001)
        self.assertRaises(SpamCError, spamc_tcp.ping)

    def test_spamc_tcp_ping(self):
        result = self.spamc_tcp.ping()
        self.assertIn('message', result)
        self.assertEqual('PONG', result['message'])

if __name__ == '__main__':
    unittest2.main()
