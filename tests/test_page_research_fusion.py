import unittest, tempfile, csv, json
from pathlib import Path
from RESEARCH_DESK import add_entry
from PAGE_RESEARCH_FUSION import match_page, fuse, save
class PageFusionTests(unittest.TestCase):
 def test_matching(self):
  self.assertTrue(match_page('https://www.facebook.com/TestPage','https://www.facebook.com/TestPage/posts/123'))
  self.assertFalse(match_page('https://www.facebook.com/TestPage','https://www.facebook.com/AnotherPage/posts/123'))
  self.assertFalse(match_page('https://www.facebook.com/TestPage','https://www.facebook.com/TestPage'))
 def test_local_join(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);add_entry(root/'ResearchDesk','https://www.facebook.com/TestPage')
   data=root/'posts.csv'
   with data.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['post_id','url','text','date']);w.writeheader();w.writerow({'post_id':'x','url':'https://www.facebook.com/TestPage/posts/123','text':'User supplied test text','date':'2026-01-01'})
   result=fuse(root,str(data))
   self.assertEqual((result['post_count'],result['matched_count'],result['page_reference_count']),(1,1,1))
   self.assertTrue(save(result,root).exists())
 def test_reference_not_post(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);add_entry(root/'ResearchDesk','https://www.facebook.com/JediSecFB')
   from RESEARCH_DESK import interactive
   # Export reference-shaped CSV without making any network call
   p=root/'sources.csv'
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['id','url','kind','verification']);w.writeheader();w.writerow({'id':'one','url':'https://www.facebook.com/JediSecFB','kind':'Page/profile or other link (unverified)','verification':'NOT FETCHED'})
   result=fuse(root,str(p))
   self.assertEqual(result['post_count'],0)
   self.assertEqual(result['import_reference_count'],1)
