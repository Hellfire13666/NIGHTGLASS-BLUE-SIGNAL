import unittest,tempfile,json
from pathlib import Path
from SOURCE_CHECK import inspect,save_report
class SourceCheckTests(unittest.TestCase):
 def test_reject_external(self):
  with self.assertRaises(ValueError):inspect('https://example.com/posts/1',lambda u:(200,None))
 def test_reject_private_route(self):
  with self.assertRaises(ValueError):inspect('https://www.facebook.com/messages/',lambda u:(200,None))
 def test_success_not_content(self):
  r=inspect('https://www.facebook.com/testpage/posts/123',lambda u:(200,None))
  self.assertFalse(r['content_collected']);self.assertIn('NOT VERIFIED',r['retrieval'])
 def test_redirect_not_followed(self):
  r=inspect('https://facebook.com/testpage/posts/1',lambda u:(302,'https://example.com/'))
  self.assertEqual(r['redirect'],'REDIRECT NOT FOLLOWED')
 def test_private_report(self):
  with tempfile.TemporaryDirectory() as d:
   p=save_report(d,inspect('https://facebook.com/testpage/posts/1',lambda u:(403,None)))
   self.assertEqual(json.loads(p.read_text())['status_code'],403)
