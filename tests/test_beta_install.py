"""Offline tests: run in temporary home dirs, NEVER touch the user's desktop."""
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('beta_install',ROOT/'scripts/beta_install.py')
import sys
sys.path.insert(0,str(ROOT/'scripts'))
beta=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(beta)

class BetaInstallTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home=Path(self.tmp.name)/'testhome'
        self.home.mkdir()
        a=self.home/'landscape.png'; a.write_bytes(b'fixture landscape')
        b=self.home/'portrait.png'; b.write_bytes(b'fixture portrait')
        self.args=SimpleNamespace(main_output='DP-6',portrait_output='DP-5',main_wallpaper=a,portrait_wallpaper=b,confirm=beta.CONFIRM_INSTALL,ack_lg_only=True)

    def test_plan_does_not_write(self):
        files=beta.contents(ROOT,self.home,self.args)
        self.assertGreater(len(files),10)
        beta.validate_home_targets(self.home,list(files),require_absent=True)
        self.assertFalse((self.home/'.config').exists())
        self.assertFalse(beta.state_path(self.home).exists())

    def test_install_rollback_roundtrip(self):
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE':''}):
            count=beta.install(self.home,self.args,check_tools=False)
            self.assertGreater(count,10)
            self.assertEqual(beta.read_state(self.home)['state'],'installed')
            self.assertEqual(beta.rollback(self.home,apply=False),count)
            self.assertEqual(beta.rollback(self.home,apply=True,confirm=beta.CONFIRM_ROLLBACK),count)
            self.assertFalse(beta.state_path(self.home).exists())
            self.assertFalse((self.home/'.config').exists())
            self.assertTrue((self.home/'landscape.png').exists())

    def test_refuses_modified_file_rollback(self):
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE':''}):
            beta.install(self.home,self.args,check_tools=False)
            a=self.home/'.config/hypr/hyprland.conf'; a.write_text('user change')
            with self.assertRaisesRegex(ValueError,'changed'):
                beta.rollback(self.home,apply=True,confirm=beta.CONFIRM_ROLLBACK)
            self.assertEqual(a.read_text(),'user change')

    def test_refuses_preexisting_file(self):
        (self.home/'.config/hypr').mkdir(parents=True)
        p=self.home/'.config/hypr/hyprland.conf'; p.write_text('keep me')
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE':''}):
            with self.assertRaisesRegex(ValueError,'overwrite'):
                beta.install(self.home,self.args,check_tools=False)
        self.assertEqual(p.read_text(),'keep me')
        self.assertFalse(beta.state_path(self.home).exists())

    def test_refuses_symlink_parent(self):
        (self.home/'.config').symlink_to(self.home/'landscape.png')
        files=beta.contents(ROOT,self.home,self.args)
        with self.assertRaisesRegex(ValueError,'symbolic link'):
            beta.validate_home_targets(self.home,list(files),require_absent=True)

    def test_refuses_active_session_and_unconfirmed(self):
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE':'fake'}):
            with self.assertRaisesRegex(ValueError,'active'):
                beta.install(self.home,self.args,check_tools=False)
        self.args.confirm='wrong'
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE':''}):
            with self.assertRaisesRegex(ValueError,'consent'):
                beta.install(self.home,self.args,check_tools=False)

    def test_manifest_path_poison_refused(self):
        with patch.dict(os.environ, {'HYPRLAND_INSTANCE_SIGNATURE':''}):
            beta.install(self.home,self.args,check_tools=False)
            rec=beta.read_state(self.home)
            rec['files'].append({'path':'.config/../../outside','sha256':'x','mode':420})
            beta.set_state(self.home,rec)
            with self.assertRaisesRegex(ValueError,'unknown'):
                beta.rollback(self.home,apply=True,confirm=beta.CONFIRM_ROLLBACK)

if __name__=='__main__': unittest.main()
