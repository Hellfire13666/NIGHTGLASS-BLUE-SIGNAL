import unittest,io,contextlib
import COMMAND_CENTER as cc
class DirectoryTests(unittest.TestCase):
 def test_all_numbers(self):
  self.assertEqual(list(cc.COMMAND_HELP), [f'{x:02}' for x in range(1,26)])
 def test_help_prints_every_number(self):
  out=io.StringIO()
  with contextlib.redirect_stdout(out): cc.command_directory()
  for i in range(1,26):self.assertIn(f'[{i:02}]',out.getvalue())
 def test_main_menu_has_all_later_numbers(self):
  out=io.StringIO()
  with contextlib.redirect_stdout(out):cc.render()
  for i in range(9,26): self.assertIn(f'[{i:02}]',out.getvalue())
if __name__=='__main__':unittest.main()
