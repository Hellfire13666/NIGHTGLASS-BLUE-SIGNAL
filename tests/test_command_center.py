import unittest
from pathlib import Path
class CommandCenterTests(unittest.TestCase):
    def test_launcher(self):
        script=(Path(__file__).resolve().parent.parent/'RUN.sh').read_text()
        self.assertIn('COMMAND_CENTER.py',script)
        self.assertIn('nightglass',script)
    def test_offline_status(self):
        script=(Path(__file__).resolve().parent.parent/'COMMAND_CENTER.py').read_text()
        self.assertIn('NOT LIVE FACEBOOK',script)
        self.assertNotIn('requests.get(',script)
