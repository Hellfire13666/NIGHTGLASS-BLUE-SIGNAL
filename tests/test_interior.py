import unittest
from unittest.mock import patch
import COMMAND_CENTER as cc
class InteriorTests(unittest.TestCase):
    def test_small_terminal(self):
        with patch('shutil.get_terminal_size',return_value=__import__('os').terminal_size((50,20))): self.assertEqual(cc.size(),60)
    def test_large_terminal(self):
        with patch('shutil.get_terminal_size',return_value=__import__('os').terminal_size((200,40))): self.assertEqual(cc.size(),100)
