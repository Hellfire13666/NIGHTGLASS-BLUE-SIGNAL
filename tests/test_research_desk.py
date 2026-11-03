import unittest, tempfile, json
from pathlib import Path
from RESEARCH_DESK import normalize, classify, add_entry, list_entries
class TestResearchDesk(unittest.TestCase):
 def test_normalization(self):
  self.assertEqual(normalize('https://www.facebook.com/example/posts/123?fbclid=tracking&utm_source=a'), 'https://www.facebook.com/example/posts/123')
 def test_story_identifiers(self):
  self.assertEqual(normalize('https://www.facebook.com/story.php?story_fbid=123&id=456&access_token=secret'), 'https://www.facebook.com/story.php?story_fbid=123&id=456')
 def test_disallowed(self):
  for url in ['http://facebook.com/a','https://evil.com/a','https://facebook.com/','https://facebook.com/messages/t/123','https://user:pass@facebook.com/a','https://facebook.com:444/a']:
   with self.assertRaises(ValueError):normalize(url)
 def test_save_dedupe(self):
  with tempfile.TemporaryDirectory() as d:
   a,created=add_entry(Path(d)/'private','https://www.facebook.com/page/posts/12','test')
   b,created2=add_entry(Path(d)/'private','https://www.facebook.com/page/posts/12?fbclid=tracker')
   self.assertTrue(created);self.assertFalse(created2);self.assertEqual(a['id'],b['id']);self.assertEqual(len(list_entries(Path(d)/'private')),1)
   self.assertEqual(a['verification'],'NOT FETCHED / UNVERIFIED')
 def test_classify(self):self.assertEqual(classify('https://www.facebook.com/page/posts/5'),'possible post link')
