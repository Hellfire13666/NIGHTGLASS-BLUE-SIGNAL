import unittest, pathlib, sys, io, contextlib
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import COMMAND_CENTER as c
class StylePush(unittest.TestCase):
 def test_module_spotlight(self):
  with contextlib.redirect_stdout(io.StringIO()) as b:c.render('04')
  self.assertIn('CROSS-REFERENCE',b.getvalue())
 def test_compact_width(self):
  with patch.object(c,'width',return_value=45),contextlib.redirect_stdout(io.StringIO()) as b:c.render('01')
  self.assertIn('COMMENT FUSION',b.getvalue())
 def test_blue_palette(self):self.assertIn('38;2;45;135;255',c.BLUE)
 def test_all_modules_annotated(self):self.assertEqual(set(c.MODULE_NOTES),{a for a,_,_ in c.ROWS})
