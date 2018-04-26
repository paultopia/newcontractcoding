from testhelperclasses import *

class TestSyncSequentialUpdate(TestStateful):
    def test_throws(self):
        self.assertEqual(1, 2)
