"""Unit tests for the repository-local, no-network helpers."""
from __future__ import annotations
import csv
import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(obj)
    return obj


publish = module(ROOT / 'scripts/prepublish.py', 'prepublish')
selected = module(ROOT / 'scripts/import_selected.py', 'import_selected')


class RepositoryChecks(unittest.TestCase):
    def create_root(self, path: Path):
        assets = path / 'assets'
        assets.mkdir()
        (assets / 'ASSET-REGISTER.csv').write_text('path,owner_or_licensor,source,permission_basis,public_distribution_approved,notes\n')
        (assets / 'THIRD-PARTY-REGISTER.csv').write_text('path,brand,rights_holder,official_terms_url,source_url,redistribution_basis,review_status,notes\n')
        (path / 'README.md').write_text('Safe public beta starter\n')

    def test_clean(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.create_root(root)
            self.assertEqual(publish.check(root), [])

    def test_unregistered_picture_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.create_root(root)
            (root / 'assets/picture.png').write_bytes(b'not a real image')
            self.assertTrue(any('not registered' in s for s in publish.check(root)))

    def test_asset_registration_needs_approval(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.create_root(root)
            (root / 'assets/picture.png').write_bytes(b'not a real image')
            with (root / 'assets/ASSET-REGISTER.csv').open('a', newline='') as out:
                csv.writer(out).writerow(['assets/picture.png', 'Kadantte', 'Original', 'Owner approval', 'no', ''])
            self.assertTrue(any('without public-distribution approval' in s for s in publish.check(root)))

    def test_secret_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            self.create_root(root)
            (root / 'id_ed25519').write_text('secret')
            self.assertTrue(any('sensitive file name' in s for s in publish.check(root)))

    def test_import_rejects_existing_destination_and_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'configs/hypr').mkdir(parents=True)
            src = root / 'example.conf'
            src.write_text('safe data')
            self.assertEqual(selected.validate(src, 'configs/hypr/new.conf', root), root / 'configs/hypr/new.conf')
            with self.assertRaises(ValueError):
                selected.validate(src, '../outside.conf', root)
            with self.assertRaises(ValueError):
                selected.validate(src, 'configs/hypr/../../outside.conf', root)
            (root / 'configs/hypr/new.conf').write_text('exists')
            with self.assertRaises(ValueError):
                selected.validate(src, 'configs/hypr/new.conf', root)


if __name__ == '__main__':
    unittest.main()

class ThirdPartyAndArchiveChecks(unittest.TestCase):
    def test_brand_binary_needs_separate_rights_clearance(self):
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            (r / 'assets/third-party').mkdir(parents=True)
            (r / 'assets/chrome.png').write_bytes(b'PNG')
            (r / 'assets/ASSET-REGISTER.csv').write_text(
                'path,owner_or_licensor,source,permission_basis,public_distribution_approved,notes\n'
                'assets/chrome.png,Google LLC,local,copied,yes,\n'
            )
            (r / 'assets/THIRD-PARTY-REGISTER.csv').write_text(
                'path,brand,rights_holder,official_terms_url,source_url,redistribution_basis,review_status,notes\n'
            )
            self.assertTrue(any('third-party image lacks separate rights record' in issue
                                for issue in publish.check(r)))

    def test_uncleared_brand_record_not_enough(self):
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            (r / 'assets/third-party').mkdir(parents=True)
            (r / 'assets/third-party/docker.png').write_bytes(b'PNG')
            (r / 'assets/ASSET-REGISTER.csv').write_text(
                'path,owner_or_licensor,source,permission_basis,public_distribution_approved,notes\n'
                'assets/third-party/docker.png,Docker Inc.,local,terms,yes,\n'
            )
            (r / 'assets/THIRD-PARTY-REGISTER.csv').write_text(
                'path,brand,rights_holder,official_terms_url,source_url,redistribution_basis,review_status,notes\n'
                'assets/third-party/docker.png,Docker,Docker Inc.,https://www.docker.com/legal/trademark-guidelines/,,,withheld,\n'
            )
            self.assertTrue(any('third-party image not cleared' in issue for issue in publish.check(r)))

    def test_brand_registry_entries_can_remain_withheld_without_binary(self):
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            (r / 'assets').mkdir(parents=True)
            (r / 'assets/ASSET-REGISTER.csv').write_text(
                'path,owner_or_licensor,source,permission_basis,public_distribution_approved,notes\n'
            )
            (r / 'assets/THIRD-PARTY-REGISTER.csv').write_text(
                'path,brand,rights_holder,official_terms_url,source_url,redistribution_basis,review_status,notes\n'
                'assets/third-party/chrome.png,Google,Google LLC,https://about.google.com,,,withheld,\n'
            )
            self.assertEqual(publish.check(r), [])

    def test_source_prefix_allowed(self):
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            s = r / 'src.txt'
            s.write_text('legit')
            self.assertEqual(selected.validate(s, 'src/shiori-v3/hud/shiori_hud.py', r),
                             r / 'src/shiori-v3/hud/shiori_hud.py')

    def test_archive_requires_exact_manifest(self):
        import zipfile
        from tempfile import NamedTemporaryFile
        archive_review = module(ROOT / 'scripts/review_source_archive.py', 'review_source_archive')
        with tempfile.TemporaryDirectory() as d:
            zpath = Path(d) / 'review.zip'
            with zipfile.ZipFile(zpath, 'w') as z:
                z.writestr('evil.sh', 'hello')
            entries, errors, _, _ = archive_review.inspect(zpath)
            self.assertTrue(errors)
            self.assertEqual(entries, {})

    def test_archive_detects_secrets_without_repeating_values(self):
        import zipfile
        archive_review = module(ROOT / 'scripts/review_source_archive.py', 'review_source_archive_2')
        with tempfile.TemporaryDirectory() as d:
            zpath = Path(d) / 'review.zip'
            with zipfile.ZipFile(zpath, 'w') as z:
                for name in archive_review.EXPECTED:
                    z.writestr(name, 'API_KEY = hidden_value\n' if name == 'src/shiori-v3/start.sh' else 'hello\n')
            entries, errors, _, secrets = archive_review.inspect(zpath)
            self.assertFalse(errors)
            self.assertEqual(len(entries), 19)
            self.assertTrue(secrets)
            self.assertTrue(all('hidden_value' not in s for s in secrets))

    def test_archive_staging_refuses_existing_target(self):
        archive_review = module(ROOT / 'scripts/review_source_archive.py', 'review_source_archive_3')
        with tempfile.TemporaryDirectory() as d:
            r = Path(d)
            existing = r / '_import-staging/source-review'
            existing.mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                archive_review.stage({'src/shiori-v3/start.sh': b'hello'}, r)
