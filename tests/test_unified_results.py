import tempfile, unittest, json
from pathlib import Path
from UNIFIED_RESULTS import installations,discover,preview
from contextlib import redirect_stdout
from io import StringIO

class UnifiedResultsTests(unittest.TestCase):
 def test_detect_known_versions_only(self):
  with tempfile.TemporaryDirectory() as t:
   h=Path(t);d=h/'Downloads';d.mkdir()
   good=d/'NIGHTGLASS-BLACKGLASS-v1.0';good.mkdir();(good/'COMMAND_CENTER.py').write_text('')
   bad=d/'PRIVATE-NOTES';bad.mkdir();(bad/'COMMAND_CENTER.py').write_text('')
   self.assertEqual(installations(h),[good])
 def test_finds_and_reads_reports(self):
  with tempfile.TemporaryDirectory() as t:
   h=Path(t);f=h/'Downloads/NIGHTGLASS-BLACKGLASS-v1.5.0';r=f/'FusionReports/demo-1';r.mkdir(parents=True)
   (f/'COMMAND_CENTER.py').write_text('')
   (r/'fusion.json').write_text(json.dumps({'posts':[{'text':'FICTIONAL data','date':'2026-10-31'}]}))
   results=discover(h);self.assertEqual(len(results),1)
   out=StringIO()
   with redirect_stdout(out):preview(results[0])
   self.assertIn('FICTIONAL data',out.getvalue())
 def test_missing_reports_is_safe(self):
  with tempfile.TemporaryDirectory() as t:self.assertEqual(discover(Path(t)),[])
 def test_symlink_report_ignored(self):
  with tempfile.TemporaryDirectory() as t:
   h=Path(t);f=h/'Downloads/NIGHTGLASS-BLACKGLASS-v1.5.0';r=f/'FusionReports/demo-1';r.mkdir(parents=True)
   (f/'COMMAND_CENTER.py').write_text('')
   other=h/'outside.json';other.write_text('{}')
   (r/'fusion.json').symlink_to(other)
   self.assertEqual(discover(h),[])
