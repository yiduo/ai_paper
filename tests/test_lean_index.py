"""Import access modifiers must not create false proof-dependency modules."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('lean_index_script', Path(__file__).resolve().parents[1]/'scripts/index_lean_closure.py')
indexer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(indexer)


class LeanIndexTests(unittest.TestCase):
    def test_access_visibility_and_comments(self):
        source = ('module\npublic import Mathlib\nimport all Mathlib.Private\n'
                  'meta import Tools.Meta\npublic meta import all Tools.Private\n'
                  '/- import Wrong.One /- public import Wrong.Two -/ -/\n'
                  'def text := "import Wrong.Three"\n')
        records = indexer.module_imports(indexer.code_only(source))
        self.assertEqual([x['module'] for x in records],
                         ['Mathlib', 'Mathlib.Private', 'Tools.Meta', 'Tools.Private'])
        self.assertEqual(records[1]['modifiers'], ['all'])
        self.assertEqual(records[3]['modifiers'], ['public', 'meta', 'all'])
        self.assertEqual(records[1]['line'], 3)

    def test_public_import_is_traversed_and_all_is_not_missing_module(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root/'math/lean/OAI';folder.mkdir(parents=True)
            (folder/'Root.lean').write_text('module\npublic import OAI.Child\nimport all Missing.Private\n')
            (folder/'Child.lean').write_text('def child : Nat := 1\n')
            result = indexer.index(root, 'OAI.Root')
            self.assertEqual({x['module'] for x in result['local_files']}, {'OAI.Root', 'OAI.Child'})
            self.assertEqual(result['external_modules_not_present'], ['Missing.Private'])
            self.assertEqual(result['local_build'], 'not_run')
