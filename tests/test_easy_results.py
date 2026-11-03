import unittest, tempfile, json
from pathlib import Path
from unittest.mock import patch
import EASY_RESULTS
class EasyResultsTests(unittest.TestCase):
 def test_empty_index(self):
  with patch.object(EASY_RESULTS,'index',return_value=[]),patch('builtins.input',side_effect=['1','0']):self.assertEqual(EASY_RESULTS.interactive(),0)
 def test_menu_returns(self):
  with patch('builtins.input',return_value='0'):self.assertEqual(EASY_RESULTS.interactive(),0)
 def test_format_report(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'report.json';p.write_text(json.dumps({'posts':[{'text':'sample','date':'2026-10-31'}]}))
   with patch.object(EASY_RESULTS,'ROOT',Path(d)):EASY_RESULTS.show_report('fusion',p)
 def test_no_network_calls(self):
  self.assertNotIn('urllib',Path(EASY_RESULTS.__file__).read_text())
