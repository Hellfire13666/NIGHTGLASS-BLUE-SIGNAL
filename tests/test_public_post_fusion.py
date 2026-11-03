import unittest,tempfile,json
from pathlib import Path
from PUBLIC_POST_FUSION import fuse,save
class FusionTests(unittest.TestCase):
 def test_import_and_source_status(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'posts.csv'
   p.write_text('post_id,date,text,url\n1,2026-10-01,Hello,https://www.facebook.com/Meta/posts/123\n1,2026-10-01,Hello,https://www.facebook.com/Meta/posts/123\n')
   result=fuse(p,tmp)
   self.assertEqual(result['input_count'],2)
   self.assertEqual(result['retained_count'],1)
   self.assertEqual(result['duplicates_removed'],1)
   self.assertFalse(result['posts'][0]['content_verified'])
 def test_source_check_not_content_verification(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'SourceChecks').mkdir();(root/'ResearchDesk').mkdir()
   url='https://www.facebook.com/Meta/posts/123'
   (root/'SourceChecks'/'source-check-x.json').write_text(json.dumps({'url':url,'status_code':200,'checked_utc':'2026-10-31T00:00:00Z'}))
   (root/'ResearchDesk'/'sources.json').write_text(json.dumps([{'url':url}]))
   p=root/'posts.csv';p.write_text('post_id,text,url\n1,Hello,'+url+'\n')
   report=fuse(p,root);item=report['posts'][0]
   self.assertEqual(item['http_status_observed'],200)
   self.assertTrue(item['research_index_match'])
   self.assertFalse(item['content_verified'])
   self.assertTrue((save(report,root)/'fusion.json').is_file())
 def test_search(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);p=root/'posts.csv';p.write_text('post_id,text\n1,Blue moon\n2,Pink sun\n')
   self.assertEqual(fuse(p,root,'blue')['retained_count'],1)
