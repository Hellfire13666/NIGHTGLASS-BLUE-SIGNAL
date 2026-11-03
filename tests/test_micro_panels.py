import unittest, io, contextlib
import COMMAND_CENTER as c
class MicroPanelTests(unittest.TestCase):
 def test_telemetry_explicit(self):
  t=c.telemetry(); self.assertEqual(t['source_mode'],'OFFLINE / IMPORT ONLY'); self.assertIn('import_count',t)
 def test_scenes(self):
  self.assertEqual(len(c.SCENES),8); self.assertTrue(all(k in c.SCENES for k in c.MODULE_NOTES))
 def test_boot(self):
  out=io.StringIO(); c.startup(out); self.assertIn('Transparent terminal preserved',out.getvalue())
 def test_render(self):
  out=io.StringIO()
  with contextlib.redirect_stdout(out): c.render('04')
  self.assertIn('SOURCE MODE',out.getvalue()); self.assertIn('LINK MAP',out.getvalue())
