import unittest, tempfile, json
from pathlib import Path
from THREAD_EXPLORER import load_report,grouped,view,interactive
class TestThreadExplorer(unittest.TestCase):
 def setUp(self):
  self.rows=[{'id':'a','parent_id':'','author':'User A','text':'hello','source':'imported'},{'id':'b','parent_id':'a','author':'User B','text':'reply keyword','source':'imported'}]
 def test_parent_reply(self):
  o=grouped(self.rows);self.assertEqual([d for d,r in o],[0,1])
 def test_filter_keeps_parent(self):
  self.assertEqual(len(grouped(self.rows,'keyword')),2)
 def test_no_match(self):
  self.assertEqual(grouped(self.rows,'nosuchword'),[])
 def test_view_status(self):
  self.assertIn('NOT LIVE',view(grouped(self.rows),0))
 def test_cycle_protection(self):
  data=[{'id':'a','parent_id':'b'},{'id':'b','parent_id':'a'}];self.assertEqual(len(grouped(data)),2)
 def test_scripted_navigation(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'report.json';path.write_text(json.dumps({'records':self.rows}))
   it=iter(['n','/','keyword','p','q']);out=[]
   self.assertEqual(interactive(path,lambda _:next(it),out.append),0)
   self.assertTrue(any('REPLY' in x for x in out))
 def test_reject_invalid_report(self):
  with tempfile.TemporaryDirectory() as t:
   path=Path(t)/'report.json';path.write_text('{"records":"bad"}')
   self.assertRaises(ValueError,load_report,path)
