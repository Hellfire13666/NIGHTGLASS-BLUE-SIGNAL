import csv, tempfile, unittest
from pathlib import Path
from POST_INTELLIGENCE import analyze_export
class SourceClassificationTests(unittest.TestCase):
    def test_reference_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'sources.csv'
            with p.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=['id','url','kind','verification','note']);w.writeheader();w.writerow({'id':'7ddafc0cf8d96095','url':'https://www.facebook.com/JediSecFB','kind':'Page/profile or other link (unverified)','verification':'NOT FETCHED / UNVERIFIED','note':'TEST ONLY'})
            r=analyze_export(p)
            self.assertEqual(r['retained_count'],0)
            self.assertEqual(r['reference_count'],1)
            self.assertEqual(r['references'][0]['reference_id'],'7ddafc0cf8d96095')
    def test_real_post_import_still_works(self):
        fixture=Path(__file__).parent.parent/'examples'/'fictional_posts.csv'
        r=analyze_export(fixture)
        self.assertEqual(r['retained_count'],2)
        self.assertEqual(r['reference_count'],0)
    def test_page_link_only_no_post(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'page.json';p.write_text('[{"post_id":"id", "url":"https://www.facebook.com/JediSecFB"}]')
            r=analyze_export(p)
            self.assertEqual(r['retained_count'],0)
            self.assertEqual(r['reference_count'],1)
