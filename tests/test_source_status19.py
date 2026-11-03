import unittest, tempfile, pathlib, json, io
from contextlib import redirect_stdout
from SOURCE_ENGINE import local_source_status
class LocalStatusTests(unittest.TestCase):
 def test_empty(self):
  with tempfile.TemporaryDirectory() as t:
   out=io.StringIO()
   with redirect_stdout(out): self.assertEqual(local_source_status(t),0)
   self.assertIn('NETWORK: OFF',out.getvalue())
 def test_http_not_approved_content(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'SourceChecks';p.mkdir()
   (p/'source-check-a.json').write_text(json.dumps({'status_code':200,'content_collected':False}))
   out=io.StringIO()
   with redirect_stdout(out):local_source_status(t)
   self.assertIn('Content collected: False',out.getvalue())
 def test_bad_json_no_crash(self):
  with tempfile.TemporaryDirectory() as t:
   p=pathlib.Path(t)/'SourceChecks';p.mkdir()
   (p/'source-check-a.json').write_text('{oops')
   out=io.StringIO()
   with redirect_stdout(out):local_source_status(t)
   self.assertIn('unreadable',out.getvalue())
