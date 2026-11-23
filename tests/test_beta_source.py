"""Static/public-beta checks. They never import GTK or execute desktop commands."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/'src/shiori-v3/icon_resolver.py'
SPEC=importlib.util.spec_from_file_location('icon_resolver',MOD)
icons=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(icons)

class FakeApp:
    def __init__(self, id, name): self.id=id;self.name=name
    def get_id(self): return self.id
    def get_name(self): return self.name
    def get_is_hidden(self): return False
    def get_nodisplay(self): return False

class BetaSourceTests(unittest.TestCase):
    def test_exact_installed_icon_priority(self):
        apps=[FakeApp('spoof.desktop','Discord Support'),FakeApp('com.discordapp.Discord.desktop','Discord')]
        self.assertIs(icons.choose_app(apps,'discord'),apps[1])

    def test_missing_icon_keeps_fallback_visible(self):
        self.assertNotIn('color: transparent',icons.css_for_icons({}))
        self.assertNotIn('background-image',icons.css_for_icons({'chrome':None}))

    def test_local_only_icon_css(self):
        with tempfile.TemporaryDirectory() as directory:
            icon=Path(directory)/'app icon.png';icon.write_bytes(b'png-test')
            css=icons.css_for_icons({'chrome':icon, 'discord':'https://invalid.test/abc.png'})
            self.assertIn('file://',css)
            self.assertIn('app%20icon.png',css)
            self.assertNotIn('https:',css)

    def test_avoid_bundled_brand_pngs(self):
        paths=[ROOT/'configs/waybar/style.css',ROOT/'src/shiori-v3/hud/shiori_hud.py']
        for p in paths:
            self.assertNotIn('v3.2-icons',p.read_text())
        for name in ('chrome.png','discord.png','docker.png'):
            self.assertFalse(any(p.name==name for p in ROOT.rglob('*') if p.is_file()))

    def test_config_templates_and_no_live_paths(self):
        for rel in ('configs/hypr/hyprland.conf','configs/hypr/hyprpaper.conf','configs/waybar/config'):
            s=(ROOT/rel).read_text()
            self.assertNotIn('/home/' + 'jaejin/',s)
            self.assertIn('{{MAIN_OUTPUT}}',s)
        json.loads((ROOT/'configs/waybar/config').read_text())

    def test_no_legacy_uncontrolled_installer(self):
        self.assertFalse((ROOT/'install.sh').exists())
        self.assertFalse((ROOT/'apply.sh').exists())

if __name__=='__main__': unittest.main()
