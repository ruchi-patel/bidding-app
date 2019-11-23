import unittest
from app import invalid_confirm_password

class TestApp(unittest.TestCase):

    def test_invalid_confirm_password(self):
        self.assertEqual(True, invalid_confirm_password(None, None))
        self.assertEqual(True, invalid_confirm_password('123', None))
        self.assertEqual(True, invalid_confirm_password(None, '111'))
        self.assertEqual(True, invalid_confirm_password('111', '123'))
        self.assertEqual(False, invalid_confirm_password('111', '111'))
        self.assertEqual(True, invalid_confirm_password('', ''))
