import translate_js
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('translate', ROOT / 'translate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class InstallSafetyTests(unittest.TestCase):
    def test_install_preserves_runtime_fields_and_restore_is_byte_exact(self):
        original = module.load_json(ROOT / 'data/package-v18-en.json')
        original['main'] = './sentinel.js'
        original['engines'] = {'vscode': 'SENTINEL'}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'package.json'
            payload = json.dumps(original, indent=3).encode()
            path.write_bytes(payload)
            with patch.object(module, 'get_gitlens_dir', return_value=Path(directory)):
                module.cmd_install()
                current = module.load_json(path)
                self.assertEqual(current['main'], './sentinel.js')
                self.assertEqual(current['engines'], {'vscode': 'SENTINEL'})
                self.assertEqual(current['version'], '18.0.0')
                self.assertNotEqual(current['contributes'], original['contributes'])
                module.cmd_restore()
            self.assertEqual(path.read_bytes(), payload)

    def test_unknown_version_and_backup_rejected_without_writes(self):
        for version in ('17.0.3', '18.1.0', '99.0.0'):
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'package.json'
                payload = json.dumps({'publisher': 'eamodio', 'name': 'gitlens', 'version': version}).encode()
                path.write_bytes(payload)
                with patch.object(module, 'get_gitlens_dir', return_value=Path(directory)):
                    with self.assertRaises(ValueError):
                        module.cmd_install()
                self.assertEqual(path.read_bytes(), payload)
                self.assertFalse(path.with_suffix('.json.backup').exists())

    def test_direct_js_apply_rejects_unknown_manifest_before_backups(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'package.json').write_text(json.dumps({'publisher': 'eamodio', 'name': 'gitlens', 'version': '99.0.0'}))
            js = root / 'dist/gitlens.js'
            js.parent.mkdir()
            js.write_bytes(b'untouched runtime')
            with patch.object(translate_js, 'find_gitlens_dirs', return_value=[root]):
                with self.assertRaises(ValueError):
                    translate_js.cmd_apply()
            self.assertEqual(js.read_bytes(), b'untouched runtime')
            self.assertFalse(js.with_suffix('.js.backup').exists())

    def test_multiple_extension_versions_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for version in ('18.0.0', '18.1.0'):
                (root / '.vscode/extensions' / f'eamodio.gitlens-{version}').mkdir(parents=True)
            with patch.object(module.Path, 'home', return_value=root):
                with self.assertRaises(ValueError):
                    module.get_gitlens_dir()

    def test_replace_failure_preserves_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'package.json'
            path.write_bytes(b'original')
            with patch.object(module.os, 'replace', side_effect=OSError('injected')):
                with self.assertRaises(OSError):
                    module.atomic_write(path, b'new')
            self.assertEqual(path.read_bytes(), b'original')


if __name__ == '__main__':
    unittest.main()
