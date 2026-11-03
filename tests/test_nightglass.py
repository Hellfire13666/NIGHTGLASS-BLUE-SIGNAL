import unittest
from nightglass.__main__ import record,dedup,compare,csv_safe
class Tests(unittest.TestCase):
 def test_dedup(self):
  r=record({'id':'abc','text':'one'},'demo');rows,n=dedup([r,r]);self.assertEqual((len(rows),n),(1,1))
 def test_conflict(self):
  a=record({'id':'abc','text':'one'},'demo');b=record({'id':'abc','text':'two'},'demo');self.assertEqual(compare([a],[b])[0]['verification_status'],'CONFLICT')
 def test_html_spreadsheet_safety(self):self.assertTrue(csv_safe('=2+2').startswith("'"))
 def test_reply(self):self.assertEqual(record({'parent_id':'123'},'demo')['parent_id'],'123')
if __name__=='__main__':unittest.main()
