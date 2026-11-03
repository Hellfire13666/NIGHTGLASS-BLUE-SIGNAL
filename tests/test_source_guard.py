import unittest,tempfile,json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from SOURCE_CHECK import guard_status,_record_guard,inspect
U='https://www.facebook.com/TestPage/posts/123'
class GuardTests(unittest.TestCase):
 def test_new(self):
  with tempfile.TemporaryDirectory() as d:self.assertTrue(guard_status(d,U)['allowed'])
 def test_cooldown(self):
  with tempfile.TemporaryDirectory() as d:
   now=datetime.now(timezone.utc)
   _record_guard(d,U,{'checked_utc':now.isoformat(),'status_code':200,'retrieval':'HTTP'})
   self.assertFalse(guard_status(d,U,now)['allowed'])
   self.assertTrue(guard_status(d,U,now+timedelta(hours=25))['allowed'])
 def test_throttle(self):
  with tempfile.TemporaryDirectory() as d:
   now=datetime.now(timezone.utc)
   _record_guard(d,U,{'checked_utc':now.isoformat(),'status_code':429,'retrieval':'RATE LIMITED'})
   self.assertFalse(guard_status(d,U,now+timedelta(hours=25))['allowed'])
   self.assertTrue(guard_status(d,U,now+timedelta(hours=73))['allowed'])
 def test_unreadable_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'source-guard.json').write_text('broken')
   self.assertFalse(guard_status(d,U)['allowed'])
 def test_no_external(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):guard_status(d,'https://example.org/page')
 def test_rate_response(self):
  result=inspect(U,lambda _: (429,None))
  self.assertIn('RATE LIMITED',result['retrieval'])
