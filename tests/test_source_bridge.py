import unittest, tempfile, json
from pathlib import Path
from SOURCE_BRIDGE import inspect_source,render_summary
class SourceBridgeTests(unittest.TestCase):
 def test_csv(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'test.csv';f.write_text('id,message\na,hello\nb,world\n')
   info=inspect_source(f)
   self.assertEqual(info['records'],2)
   self.assertTrue(info['schema_detected'])
   self.assertIn('NO NETWORK',render_summary(info))
 def test_json(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'test.json';f.write_text(json.dumps({'data':[{'id':'1'},{'id':'2'}]}))
   self.assertEqual(inspect_source(f)['records'],2)
 def test_jsonl(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'test.jsonl';f.write_text('{"id":1}\n{"id":2}\n')
   self.assertEqual(inspect_source(f)['records'],2)
 def test_invalid(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'test.json';f.write_text('not json')
   with self.assertRaises(ValueError):inspect_source(f)
 def test_reject_unrecognized_type(self):
  with tempfile.TemporaryDirectory() as d:
   f=Path(d)/'test.txt';f.write_text('hi')
   with self.assertRaises(ValueError):inspect_source(f)
if __name__=='__main__':unittest.main()
