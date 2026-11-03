import unittest,tempfile,json
from pathlib import Path
from THREAD_FUSION import make_tree,describe,explore
class FusionTests(unittest.TestCase):
 def setUp(self):
  self.rows=[{'id':'a','author':'Root','text':'hello'}, {'id':'b','parent_id':'a','author':'Child','text':'needle'}, {'id':'c','parent_id':'missing','author':'Lost','text':'orphan'}, {'id':'d','author':'Another','text':'rest'}]
 def test_depth(self):
  tree=make_tree(self.rows);self.assertEqual([x['key'] for x in tree],['a','b','d','c']);self.assertEqual(tree[1]['depth'],1)
 def test_parent_filter(self):self.assertEqual([x['key'] for x in make_tree(self.rows,'needle')],['a','b'])
 def test_orphan(self):self.assertIn('ORPHAN',describe(make_tree(self.rows),3))
 def test_no_match(self):self.assertEqual(make_tree(self.rows,'not-there'),[])
 def test_interactive(self):
  with tempfile.TemporaryDirectory() as t:
   f=Path(t)/'report.json';f.write_text(json.dumps({'records':self.rows}))
   answers=iter(['t','r','u','/','needle','n','c','q']);lines=[]
   self.assertEqual(explore(f,lambda prompt:next(answers),lines.append),0)
   self.assertTrue(any('THREAD FUSION' in x for x in lines))
