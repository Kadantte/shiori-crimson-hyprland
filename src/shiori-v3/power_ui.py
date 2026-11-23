#!/usr/bin/python3
"""Shiori Crimson v3.3.2 GTK3+layer-shell power UI.

Preview mode never runs a power action. A separate confirmation screen is
required for every real action. No shell interpolation or background work.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

if len(sys.argv) != 1 and sys.argv[1:] not in (['--preview'], ['--probe']):
    sys.exit('Usage: power_ui.py [--preview|--probe]')
PREVIEW = '--preview' in sys.argv

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib, GtkLayerShell

if not GtkLayerShell.is_supported():
    sys.exit('Layer shell unsupported in this session')
if '--probe' in sys.argv:
    sys.exit(0)
if not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
    sys.exit('Shiori power menu is only available under Hyprland')

ROOT = Path(__file__).resolve().parent
ASSET = ROOT / 'assets' / 'shiori-menu-portrait.png'
LOG = Path(os.environ.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'shiori-v3.3.2-power.log'
PALETTE = {'crimson':'#D5232A', 'gold':'#F4B845', 'ivory':'#FFF0D4'}

CSS = r'''
* { font-family:"Noto Sans", "Ubuntu", sans-serif; color:#FFF0D4; }
window { background-color:transparent; }
.power-shell { background-color:rgba(18,13,17,.98); border:2px solid #D5232A; border-radius:24px; padding:25px; }
.power-side { background-color:#22151C; border:1px solid rgba(244,184,69,.5); border-radius:16px; padding:10px; }
.power-kicker { font-size:13px; font-weight:800; color:#F4B845; letter-spacing:2px; }
.power-title { font-size:35px; font-weight:900; color:#FFF0D4; }
.power-desc { font-size:15px; color:#EABFC5; }
.power-section { font-size:13px; font-weight:900; color:#F4B845; }
.power-action { border:1px solid rgba(182,61,73,.65); border-radius:14px; background-color:rgba(66,25,39,.88); padding:13px; min-width:196px; min-height:65px; }
.power-action:hover, .power-action:focus { background-color:rgba(144,33,52,.96); border-color:#F4B845; }
.power-action:disabled { background-color:rgba(50,40,43,.45); border-color:#55464B; }
.power-danger { border-color:rgba(213,35,42,.85); }
.power-action-title { font-size:19px; font-weight:800; color:#FFECE6; }
.power-action-desc { font-size:12px; color:#D7ACB5; }
.power-footer { font-size:12px; color:#C6A5AB; }
.power-muted { font-size:13px; color:#D3B3B9; }
.power-portrait { border:1px solid rgba(244,184,69,.55); border-radius:12px; padding:3px; }
.power-separator { background-color:#77313E; min-height:1px; }
.power-back { border:1px solid #7D5259; border-radius:10px; background-color:#292023; padding:12px 24px; }
.power-confirm { border:1px solid #F4B845; border-radius:10px; background-color:#A52B40; padding:12px 24px; }
.power-confirm:hover { background-color:#D5232A; }
.power-preview { color:#F4B845; font-size:13px; font-weight:700; }
'''

provider = Gtk.CssProvider()
provider.load_from_data(CSS.encode())
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
                                         Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

def note(message):
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open('a', encoding='utf-8') as f:
            f.write(f'{datetime.now().isoformat(timespec="seconds")} {message}\n')
    except OSError:
        pass

def text(content, klass, align=0):
    label=Gtk.Label(label=content, xalign=align)
    label.get_style_context().add_class(klass)
    label.set_line_wrap(True)
    return label

def col(space=8):
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=space)

def row(space=8):
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=space)

def button(title, subtitle, callback, style='power-action'):
    b=Gtk.Button()
    b.get_style_context().add_class(style)
    inner=col(4)
    inner.pack_start(text(title,'power-action-title'),False,False,0)
    if subtitle: inner.pack_start(text(subtitle,'power-action-desc'),False,False,0)
    b.add(inner)
    b.connect('clicked',lambda *_:callback())
    return b

class PowerWindow:
    COMMANDS = {
        'Log Out': ['hyprctl','dispatch','exit'],
        'Restart': ['systemctl','reboot'],
        'Shut Down': ['systemctl','poweroff'],
    }
    DESCRIPTIONS = {
        'Lock Screen':'Secure Asura without ending the session.',
        'Log Out':'End this Hyprland session. Save your work first.',
        'Restart':'Restart Asura. All unsaved work will be lost.',
        'Shut Down':'Power off Asura. All unsaved work will be lost.',
    }
    def __init__(self):
        self.selection=None
        display=Gdk.Display.get_default()
        lg=None
        # Reuse Shiori's known LG identity; don't change display rules or output geometry.
        for i in range(display.get_n_monitors()):
            candidate=display.get_monitor(i)
            ident=((candidate.get_model() or '')+' '+(candidate.get_manufacturer() or '')).upper()
            if 'ULTRAGEAR' in ident or 'LG ELECTRONICS' in ident or 'LG ' in ident:
                lg=candidate
                break
        if lg is None:
            raise RuntimeError('LG monitor not identified; refusing to place menu on ASUS')
        self.win=Gtk.Window(title='Shiori Crimson · Power')
        self.win.set_decorated(False)
        self.win.set_resizable(False)
        self.win.set_app_paintable(True)
        rgba=self.win.get_screen().get_rgba_visual()
        if rgba: self.win.set_visual(rgba)
        self.win.set_default_size(750,530)
        GtkLayerShell.init_for_window(self.win)
        GtkLayerShell.set_namespace(self.win,'shiori-power-menu')
        GtkLayerShell.set_monitor(self.win,lg)
        GtkLayerShell.set_layer(self.win,GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_exclusive_zone(self.win,0)
        # Zero anchors is protocol-defined center of monitor.
        GtkLayerShell.set_keyboard_mode(self.win,GtkLayerShell.KeyboardMode.EXCLUSIVE)
        self.win.connect('key-press-event',self.key_pressed)
        self.win.connect('delete-event',lambda *_: self.close() or True)

        outer=col(0)
        outer.get_style_context().add_class('power-shell')
        outer.set_size_request(750,530)
        self.stack=Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(180)
        self.main=self.make_main()
        self.confirm=self.make_confirm()
        self.stack.add_named(self.main,'main')
        self.stack.add_named(self.confirm,'confirm')
        outer.pack_start(self.stack,True,True,0)
        self.win.add(outer)
        self.stack.set_visible_child_name('main')
        self.win.show_all()
        self.stack.set_visible_child_name('main')

    def make_main(self):
        content=row(23)
        left=col(17)
        left.pack_start(text('✦  SHIORI CRIMSON  //  SYSTEM','power-kicker'),False,False,0)
        left.pack_start(text('ASURA  ·  POWER','power-title'),False,False,0)
        left.pack_start(text('Rest beneath the crimson moon, or choose your next journey.','power-desc'),False,False,0)
        left.pack_start(text('SESSION CONTROLS','power-section'),False,False,6)
        tiles=Gtk.Grid()
        tiles.set_row_spacing(12)
        tiles.set_column_spacing(12)
        items=[('Lock Screen','Secure your session','◈'),
               ('Log Out','Return to login','↪'),
               ('Restart','Reboot Asura','⟳'),
               ('Shut Down','Power off safely','⏻')]
        lock_available=bool(shutil.which('hyprlock') or shutil.which('swaylock'))
        for idx,(name,subtitle,glyph) in enumerate(items):
            b=button(f'{glyph}  {name}',subtitle,lambda n=name:self.choose(n))
            if name=='Shut Down': b.get_style_context().add_class('power-danger')
            if name=='Lock Screen' and not lock_available:
                b.set_sensitive(False)
                b.set_tooltip_text('Install hyprlock or swaylock to enable locking')
            tiles.attach(b,idx%2,idx//2,1,1)
        left.pack_start(tiles,False,False,0)
        status='PREVIEW MODE  ·  NO POWER ACTIONS POSSIBLE' if PREVIEW else 'No action is performed until you confirm.'
        left.pack_end(text(status,'power-preview' if PREVIEW else 'power-footer'),False,False,0)
        cancel=Gtk.Button(label='Cancel  ·  Esc')
        cancel.get_style_context().add_class('power-back')
        cancel.connect('clicked',lambda *_:self.close())
        left.pack_end(cancel,False,False,0)
        content.pack_start(left,True,True,0)
        side=col(13)
        side.get_style_context().add_class('power-side')
        if ASSET.is_file():
            try:
                pix=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(ASSET),192,309,True)
                img=Gtk.Image.new_from_pixbuf(pix)
                img.get_style_context().add_class('power-portrait')
                side.pack_start(img,False,False,0)
            except GLib.Error:
                pass
        side.pack_start(text('SHIORI-CHAN  ♡','power-kicker',.5),False,False,0)
        side.pack_start(text('Keep your work safe.','power-muted',.5),False,False,0)
        content.pack_end(side,False,False,0)
        return content

    def make_confirm(self):
        content=col(19)
        content.pack_start(text('✦  SHIORI CRIMSON  //  CONFIRMATION','power-kicker'),False,False,0)
        self.confirm_title=text('Confirm action','power-title')
        content.pack_start(self.confirm_title,False,False,0)
        self.confirm_desc=text('','power-desc')
        content.pack_start(self.confirm_desc,False,False,0)
        content.pack_start(text('This action will only run after explicit confirmation.','power-muted'),False,False,10)
        self.confirm_status=text('','power-preview')
        content.pack_start(self.confirm_status,False,False,0)
        buttons=row(16)
        back=Gtk.Button(label='←  Back')
        back.get_style_context().add_class('power-back')
        back.connect('clicked',lambda *_: self.stack.set_visible_child_name('main'))
        buttons.pack_start(back,False,False,0)
        self.confirm_button=Gtk.Button(label='Confirm')
        self.confirm_button.get_style_context().add_class('power-confirm')
        self.confirm_button.connect('clicked',lambda *_:self.execute())
        buttons.pack_end(self.confirm_button,False,False,0)
        content.pack_end(buttons,False,False,0)
        return content

    def choose(self,selection):
        if selection not in self.DESCRIPTIONS: return
        self.selection=selection
        self.confirm_title.set_text(f'{selection} Asura?')
        self.confirm_desc.set_text(self.DESCRIPTIONS[selection])
        self.confirm_status.set_text('PREVIEW: This action will NOT run.' if PREVIEW
                                     else 'Review your choice before continuing.')
        self.confirm_button.set_label('Close Preview' if PREVIEW else f'Confirm {selection}')
        self.stack.set_visible_child_name('confirm')
        note(f'selected: {selection} (preview={PREVIEW})')

    def execute(self):
        if self.selection not in self.DESCRIPTIONS:
            return
        if PREVIEW:
            note(f'preview no-op: {self.selection}')
            self.close()
            return
        if self.selection=='Lock Screen':
            cmd=[shutil.which('hyprlock') or shutil.which('swaylock')]
            if not cmd[0]:
                note('Lock screen unavailable')
                self.close()
                return
        else:
            cmd=self.COMMANDS[self.selection]
            if self.selection=='Log Out' and not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
                note('Refusing logout outside Hyprland')
                self.close()
                return
        note(f'confirmed: {self.selection}; command={cmd[0]}')
        try:
            subprocess.Popen(cmd,stdin=subprocess.DEVNULL,
                             stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                             start_new_session=True)
        except OSError as e:
            note(f'launch failed: {e}')
        self.close()

    def key_pressed(self, _widget, event):
        if event.keyval==Gdk.KEY_Escape:
            if self.stack.get_visible_child_name()=='confirm':
                self.stack.set_visible_child_name('main')
            else:
                self.close()
            return True
        return False

    def close(self):
        Gtk.main_quit()
        return True

if __name__=='__main__':
    try:
        window=PowerWindow()
        Gtk.main()
    except Exception as exc:
        note(f'power UI error: {exc!r}')
        print('Shiori power UI:',exc,file=sys.stderr)
        raise
