import unittest, tempfile, json
from pathlib import Path
import REPORT_DECK as r
class ReportDeckTests(unittest.TestCase):
 def test_types(self):self.assertIn('fusion',r.TYPES)
 def test_missing(self):
  from unittest.mock import patch
  with patch.object(r, 'ROOT', self._empty_root()): self.assertIsNone(r.latest('fusion'))
 def _empty_root(self):
  import tempfile
  self.addCleanup(self._cleanup_temp)
  self._temp=tempfile.TemporaryDirectory()
  return Path(self._temp.name)
 def _cleanup_temp(self):self._temp.cleanup()
 def test_explicit_source_dir(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'source-check-a.json';p.write_text(json.dumps({'status_code':200}))
   self.assertEqual(len(r.reports('source',d)),1)
 def test_no_default_external(self):
  self.assertEqual(r.reports('source', '/nonexistent/nightglass/path'),[])
