import unittest, pathlib, sys, io, contextlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import COMMAND_CENTER as bg
class BlackglassTests(unittest.TestCase):
 def test_compact(self):
  self.assertEqual(len(bg.ROWS),8)
 def test_local_path(self):
  self.assertTrue((bg.ROOT/'examples'/'fictional_comments.csv').is_file())
 def test_render(self):
  buf=io.StringIO()
  with contextlib.redirect_stdout(buf):bg.render()
  self.assertIn('OFFLINE',buf.getvalue())
 def test_safe_exit(self):
  from unittest.mock import patch
  with patch('builtins.input',return_value='00'),contextlib.redirect_stdout(io.StringIO()):
   self.assertEqual(bg.menu(),0)
