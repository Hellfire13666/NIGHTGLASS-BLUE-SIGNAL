import unittest, tempfile, json
from pathlib import Path
from SOURCE_ENGINE import analyze_snapshot, save_snapshot
class SourceEngineTests(unittest.TestCase):
 def test_meta(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.html';p.write_text('<html><head><title>Example page</title><meta property="og:title" content="Public Title"></head></html>')
   result=analyze_snapshot(p,'https://www.facebook.com/Meta')
   self.assertEqual(result['metadata']['og:title'],'Public Title')
   self.assertEqual(result['posts'],[])
   self.assertFalse(result['content_verified'])
   saved=save_snapshot(result,Path(d)/'reports')
   self.assertTrue(saved.exists())
 def test_bad_scheme(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.html';p.write_text('ok')
   with self.assertRaises(ValueError):analyze_snapshot(p,'http://facebook.com/Meta')
 def test_not_html(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'a.txt';p.write_text('ok')
   with self.assertRaises(ValueError):analyze_snapshot(p)
