import unittest
import src.az 

class AzTest(unittest.TestCase):

    def setUp(self):
        self.az = src.az.Az()

    def test_create_and_delete_a_secret(self):
        self.az.update_secret("test", "test-string")
        self.assertEqual(self.az.get_secret("test"), "test-string")
        self.az.delete_secret("test")