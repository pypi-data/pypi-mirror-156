import mock
import sys
from io import StringIO

from tests.ModuleBaseTestCase import ModuleBaseTestCase, MockLumberMill
from lumbermill.input import StdIn


class TestStdIn(ModuleBaseTestCase):

    def setUp(self):
        super(TestStdIn, self).setUp(StdIn.StdIn(mock.Mock()))

    def testStdInSingleLine(self):
        self.test_object.configure({})
        input = StringIO("We are the knights who say ni!")
        stdin = sys.stdin
        sys.stdin = input
        self.test_object.run()
        sys.stdin = stdin
        for event in self.receiver.getEvent():
            self.assertEqual(event['data'], "We are the knights who say ni!")

    def testStdInMultiLine(self):
        self.test_object.configure({'multiline': True})
        input = StringIO("""We are the knights who say ni!
Bring us a shrubbery!""")
        stdin = sys.stdin
        sys.stdin = input
        self.test_object.run()
        sys.stdin = stdin
        for event in self.receiver.getEvent():
            self.assertEqual(event['data'], """We are the knights who say ni!
Bring us a shrubbery!""")        

    def testStdInStreamBoundry(self):
        self.test_object.configure({'multiline': True,
                                    'stream_end_signal': "Ekki-Ekki-Ekki-Ekki-PTANG\n"})
        self.checkConfiguration()
        input = StringIO("""We are the knights who say ni!
Bring us a shrubbery!
Ekki-Ekki-Ekki-Ekki-PTANG
We are now no longer the Knights who say Ni.""")
        stdin = sys.stdin
        sys.stdin = input
        self.test_object.run()
        sys.stdin = stdin
        item = []
        for event in self.receiver.getEvent():
            item.append(event)
        self.assertEqual(len(item), 2)
        self.assertEqual(item[0]['data'], """We are the knights who say ni!
Bring us a shrubbery!\n""")
        self.assertEqual(item[1]['data'], "We are now no longer the Knights who say Ni.")