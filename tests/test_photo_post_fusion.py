import unittest,tempfile,csv,json
from pathlib import Path
from PHOTO_POST_FUSION import fuse,read_records,save,photo_id
class TestPhotoFusion(unittest.TestCase):
 def setUp(self):self.src={'id':'ref123','url':'https://www.facebook.com/photo.php?fbid=122147963997231709','kind':'possible photo link'}
 def test_id(self):self.assertEqual(photo_id(self.src['url']),'122147963997231709')
 def test_empty(self):
  x=fuse(self.src);self.assertEqual(x['network_requests'],0);self.assertEqual(x['comment_count'],0);self.assertEqual(x['caption'],'')
 def test_matches_and_replies(self):
  p=[{'post_id':'122147963997231709','text':'Own caption','date':'2026-10-31'}]
  c=[{'comment_id':'1','post_id':'122147963997231709','text':'Hello'},{'comment_id':'1','post_id':'122147963997231709','text':'Hello'},{'comment_id':'2','post_id':'122147963997231709','parent_id':'1','text':'Reply'},{'comment_id':'3','post_id':'unrelated','text':'Skip'}]
  x=fuse(self.src,p,c);self.assertEqual(x['caption'],'Own caption');self.assertEqual(x['comment_count'],2);self.assertEqual(x['reply_count'],1);self.assertEqual(x['skipped_or_duplicate_comments'],2)
 def test_file_roundtrip(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'posts.csv';p.write_text('post_id,text\n122147963997231709,hi\n')
   rows,h=read_records(p);self.assertEqual(len(rows),1);self.assertEqual(len(h),64)
   out=save(fuse(self.src,rows),Path(t)/'reports');self.assertEqual(json.loads(out.read_text())['post_match_count'],1)
 def test_wrong_suffix(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/'bad.txt';p.write_text('oops')
   with self.assertRaises(ValueError):read_records(p)
if __name__=='__main__':unittest.main()
