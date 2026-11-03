import unittest,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE if (HERE/"COMMAND_CENTER.py").is_file() else HERE.parent
class EasyModeTests(unittest.TestCase):
 def test_demo_and_latest_without_filename(self):
  proc=subprocess.run([sys.executable,'COMMAND_CENTER.py'],input='20\n21\n00\n',text=True,capture_output=True,cwd=ROOT,timeout=20)
  self.assertEqual(proc.returncode,0,proc.stderr)
  self.assertIn('EASY MODE',proc.stdout)
  self.assertIn('FICTIONAL test post',proc.stdout)
  self.assertIn('BLACKGLASS closed safely',proc.stdout)
 def test_easy_menu_visible(self):
  proc=subprocess.run([sys.executable,'COMMAND_CENTER.py','--snapshot'],capture_output=True,text=True,cwd=ROOT,timeout=10)
  self.assertIn('[20] EASY DEMO',proc.stdout)
  self.assertIn('[21] READ LATEST',proc.stdout)
