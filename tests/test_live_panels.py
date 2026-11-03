import unittest, tempfile, json, io, contextlib
from pathlib import Path
from unittest.mock import patch
import COMMAND_CENTER as c
class LivePanelsTests(unittest.TestCase):
 def test_demo_updates_counts_from_actual_report(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   with patch.object(c,'ROOT',root),patch.object(c,'STATE_FILE',root/'.state.json'):
    with patch.object(c,'SESSION',dict(c.SESSION)):
     with patch.object(c,'engine',side_effect=lambda argv: fake_engine(argv,root)):
      with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.analyze('demo',[]),0)
      self.assertEqual(c.SESSION['import_count'],'4')
      self.assertEqual(c.SESSION['unique_count'],'3')
      self.assertEqual(c.SESSION['duplicate_count'],'1')
      self.assertEqual(c.SESSION['reply_count'],'1')
      self.assertTrue((root/'.state.json').exists())
 def test_failure_does_not_change_session(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   with patch.object(c,'ROOT',root),patch.object(c,'SESSION',dict(c.SESSION)),patch.object(c,'engine',return_value=2):
    before=dict(c.SESSION)
    with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(c.analyze('demo',[]),2)
    self.assertEqual(before,c.SESSION)
 def test_state_private_no_input_paths(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)
   with patch.object(c,'STATE_FILE',root/'state.json'),patch.object(c,'SESSION',dict(c.SESSION)):
    c.save_state();raw=(root/'state.json').read_text()
    self.assertNotIn('author',raw);self.assertNotIn('input_path',raw)
 def test_menu_has_micropanels(self):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):c.render('01')
  self.assertIn('REPLIES',out.getvalue())
  self.assertIn('TEST STATUS',out.getvalue())
def fake_engine(argv,root):
 out=root/argv[argv.index('--out')+1];out.mkdir(parents=True)
 (out/'report.json').write_text(json.dumps({'records':[{'parent_id':''},{'parent_id':'1'},{'parent_id':''}], 'metadata':{'original_count':4,'duplicates_removed':1}}))
 return 0
