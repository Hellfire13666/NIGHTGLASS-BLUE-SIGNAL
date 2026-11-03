import unittest,tempfile,json
from pathlib import Path
from POST_INTELLIGENCE import analyze_export,save_private
class PostIntelligenceTests(unittest.TestCase):
 def test_fixture(self):
  d=Path(__file__).resolve().parent.parent
  r=analyze_export(d/'examples/fictional_posts.csv')
  self.assertEqual(r['retained_count'],2)
  self.assertEqual(r['source'],'USER-SUPPLIED LOCAL FILE')
 def test_keyword(self):
  d=Path(__file__).resolve().parent.parent
  self.assertEqual(analyze_export(d/'examples/fictional_posts.csv','research')['retained_count'],1)
 def test_reject_other(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'x.txt';p.write_text('hello')
   with self.assertRaises(ValueError):analyze_export(p)
 def test_private(self):
  with tempfile.TemporaryDirectory() as d:
   report={'posts':[{'post_id':'1','date':'','text':'example','url':'','source_mode':'IMPORTED'}]}
   folder=save_private(report,Path(d)/'reports')
   self.assertTrue((folder/'posts.json').exists())
   self.assertEqual(json.loads((folder/'posts.json').read_text())['posts'][0]['post_id'],'1')
