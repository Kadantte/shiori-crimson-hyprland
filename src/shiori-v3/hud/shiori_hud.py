#!/usr/bin/python3
"""Shiori Crimson v3 user-session HUD. GTK3 + gtk-layer-shell (Ubuntu packages).
Does not alter monitors, GPU, input or audio settings.
"""
import os
import sys
import socket
import subprocess
import time
import datetime
import threading
import urllib.request
import urllib.parse
from pathlib import Path

RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
SOCKET = RUNTIME / "shiori-crimson-v3.sock"
HOME = Path.home()
ASSETS = HOME / ".config/shiori-v3/assets"


def send(command):
    try:
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(.8)
            sock.connect(str(SOCKET))
            sock.sendall(command.encode('utf-8'))
            return 0
    except (ConnectionRefusedError, FileNotFoundError, OSError):
        return 1


if len(sys.argv) > 1:
    sys.exit(send(sys.argv[1]))

if not os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
    sys.exit('Shiori HUD requires a Hyprland session. GNOME is untouched.')

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, Gio, GLib, GtkLayerShell, Pango, GdkPixbuf
# SHIORI_CRIMSON_333_APP_CATALOG — desktop entries and XDG application discovery
sys.path.insert(0, str(HOME / '.config/shiori-v3'))
from app_catalog import discover as shiori_discover_apps, search as shiori_search_apps, is_settings as shiori_is_settings

try:
    import psutil
except ImportError:
    sys.exit('python3-psutil is required; install using apt.')

if not GtkLayerShell.is_supported():
    sys.exit('Wayland layer-shell protocol unavailable; exiting without changes.')

CSS = r'''
* { font-family: "Noto Sans", "Ubuntu", sans-serif; color:#fce9eb; font-size: 18px; }
window { background-color: transparent; }
.card { background-color: rgba(19,14,17,.92); border:1px solid rgba(195,48,64,.84); border-radius:21px; padding:18px; }
.card-title { font-size:22px; font-weight:800; margin-bottom:11px; }
.small { font-size:15px; color:#bbabb1; }
.muted { font-size:15px; color:#dbb5bf; }
.number {font-size: 19px; font-weight:700; color:#f2ced1; }
.bigclock {font-size:69px; font-weight:500; color:white;}
.clock-date {font-size:20px; color:#f4dfe0; }
.quote {font-size:19px; font-style:italic; color:#ffe4e8;}
.progress trough { background-color: rgba(82,49,55,.9); border-radius:8px; min-height:9px; }
.progress progress { background-image:linear-gradient(to right,#92364b,#f35b81); border-radius:8px; min-height:9px; }
.bar-label {font-size:16px; color:#f3e1e3; }
.music-title {font-size:21px; font-weight:800;}
.media-button { border:1px solid rgba(173,61,77,.55); border-radius:100px; padding:8px; min-width:38px; min-height:35px; background-color:rgba(39,23,31,.85); }
.media-button.media-primary { background-color:#ad293d; border-color:#e45b70; }
.media-button.snapshot-button { border-radius:12px; min-height:24px; font-size:15px; background-color:rgba(72,30,44,.68); }
.media-button:hover {background-color:rgba(190,49,63,.68);}
.media-button label {font-size:23px;}
.launcher-search {border-radius:12px; background-color:rgba(22,18,20,.95); border:1px solid rgba(116,38,48,.75); padding:12px 15px; color:white;}
.launcher-search:focus {border:1px solid #c7475b;}
.launch-row {border:none; background-color:transparent; border-radius:12px; padding:9px 13px;}
.launch-row:hover, .launch-row:focus {background-color:rgba(167,45,58,.65);}
.launch-name {font-weight:600; font-size:18px;}
.menu-caption {font-size:14px; color:#e5bdc1;}
/* SHIORI_CRIMSON_332_LAUNCHER — scoped to launcher widgets only */
.launcher-shell { background-color:rgba(18,13,17,.98); border:2px solid #D5232A; border-radius:23px; padding:23px; }
.launcher-hero { background-image:linear-gradient(to right,rgba(84,20,34,.95),rgba(37,18,29,.86)); border:1px solid rgba(244,184,69,.36); border-radius:17px; padding:13px 17px; }
.launcher-kicker { font-size:13px; font-weight:800; letter-spacing:2px; color:#F4B845; }
.launcher-brand { font-size:31px; font-weight:900; color:#FFF0D4; }
.launcher-subtitle { font-size:15px; color:#F4C6C7; }
.launcher-tag { font-size:13px; color:#F4B845; }
.launcher-art { background-color:rgba(14,10,14,.78); border:1px solid rgba(244,184,69,.65); border-radius:13px; padding:3px; }
.launcher-search { font-size:19px; min-height:41px; border:1px solid rgba(244,184,69,.54); border-radius:13px; padding:9px 14px; background-color:#242021; color:#FFF0D4; }
.launcher-search:focus { border-color:#F4B845; background-color:#2A1B24; }
.launcher-section { font-size:13px; font-weight:800; color:#F4B845; }
.launcher-hint { font-size:13px; color:#CDAFB4; }
.launcher-pin { border:1px solid rgba(176,55,70,.55); border-radius:13px; background-color:rgba(49,24,34,.88); padding:9px 6px; }
.launcher-pin:hover, .launcher-pin:focus { background-color:rgba(154,40,58,.9); border-color:#F4B845; }
.launcher-pin-label { font-size:13px; font-weight:700; color:#FFE7DF; }
.launcher-results { background-color:rgba(27,19,24,.85); border:1px solid rgba(114,39,50,.6); border-radius:13px; padding:6px; }
.launch-row { border:1px solid transparent; border-radius:11px; background-color:transparent; padding:9px 12px; }
.launch-row:hover, .launch-row:focus { background-color:rgba(149,40,58,.85); border-color:rgba(244,184,69,.5); }
.launch-name { font-size:16px; font-weight:800; color:#FFF0D4; }
.launch-desc { font-size:12px; color:#D3AFB7; }
.launch-arrow { font-size:18px; color:#F4B845; }
.launcher-footer { font-size:12px; color:#C7A8AF; }
'''
provider = Gtk.CssProvider()
provider.load_from_data(CSS.encode('utf-8'))
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def run(*args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=3).stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ''


def label(text, css='', xalign=0):
    l = Gtk.Label(label=str(text), xalign=xalign)
    if css:
        l.get_style_context().add_class(css)
    return l


def box(vertical=True, spacing=0):
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL if vertical else Gtk.Orientation.HORIZONTAL, spacing=spacing)


def padbox(w, margin=0):
    w.set_border_width(margin)
    return w


def row_pair(left_text, right_text):
    row=box(False, 8)
    row.pack_start(label(left_text, 'bar-label'), False, False, 0)
    right=label(right_text,'muted', 1)
    row.pack_end(right, False, False, 0)
    return row, right


def button(text, callback, tooltip=None):
    b=Gtk.Button()
    b.add(label(text))
    b.get_style_context().add_class('media-button')
    b.connect('clicked',lambda *_:callback())
    if tooltip: b.set_tooltip_text(tooltip)
    return b


def window(name, monitor, width, height, top=None, left=None, right=None, bottom=None,
           layer=GtkLayerShell.Layer.BOTTOM, keyboard=False):
    w=Gtk.Window(title=name)
    w.set_name(name)
    w.set_decorated(False)
    w.set_resizable(False)
    w.set_app_paintable(True)
    visual=w.get_screen().get_rgba_visual()
    if visual: w.set_visual(visual)
    w.set_default_size(width,height)
    GtkLayerShell.init_for_window(w)
    GtkLayerShell.set_namespace(w,'shiori-'+name)
    GtkLayerShell.set_monitor(w,monitor)
    GtkLayerShell.set_layer(w,layer)
    GtkLayerShell.set_exclusive_zone(w,0)
    for edge,amount in [(GtkLayerShell.Edge.TOP,top),(GtkLayerShell.Edge.LEFT,left),
                        (GtkLayerShell.Edge.RIGHT,right),(GtkLayerShell.Edge.BOTTOM,bottom)]:
        if amount is not None:
            GtkLayerShell.set_anchor(w,edge,True)
            GtkLayerShell.set_margin(w,edge,int(amount))
    GtkLayerShell.set_keyboard_mode(w,GtkLayerShell.KeyboardMode.ON_DEMAND if keyboard else GtkLayerShell.KeyboardMode.NONE)
    w.connect('delete-event',lambda *_: w.hide() or True)
    return w


def card(content, width, height):
    outer=box(True, 8)
    outer.get_style_context().add_class('card')
    outer.set_size_request(width,height)
    outer.pack_start(content,True,True,0)
    return outer


def find_lg():
    display=Gdk.Display.get_default()
    models=[]
    for i in range(display.get_n_monitors()):
        m=display.get_monitor(i)
        name=(m.get_model() or '')+' '+(m.get_manufacturer() or '')
        models.append(name)
        if 'ULTRAGEAR' in name.upper() or 'LG ' in name.upper() or 'LG ELECTRONICS' in name.upper():
            return m
    raise RuntimeError('LG monitor could not be identified: '+repr(models)+'; HUD not started to avoid placing widgets on ASUS')


class ShioriHud:
    def __init__(self):
        self.lg=find_lg()
        self.windows=[]
        self.setup_right_column()
        self.setup_launcher()
        self.make_socket()
        for w in self.windows: w.show_all()
        self.launcher.hide()
        psutil.cpu_percent(None)
        GLib.timeout_add_seconds(3,self.refresh_resources)
        GLib.timeout_add_seconds(4,self.refresh_music)
        GLib.timeout_add_seconds(10,self.refresh_clock)
        self.refresh_resources()
        # Read GPU/VRAM once after GTK main loop starts; thereafter refresh only on click.
        GLib.idle_add(self.refresh_gpu)
        self.refresh_music()
        self.refresh_clock()

    def setup_right_column(self):
        # All right-side cards share ONE layer-shell window and a vertical GTK box.
        # They can grow with fonts/text without ever overlapping one another.
        w = window('dashboard', self.lg, 540, -1, top=82, right=24)
        column = box(True, 18)
        self.setup_resources(column)
        self.setup_music(column)
        self.setup_clock(column)
        w.add(column)
        self.windows.append(w)

    def setup_resources(self, column):
        content=box(True,8)
        content.pack_start(label('▣  Resources','card-title'),False,False,0)
        self.progress=[]
        for title in ['CPU','Memory','GPU (RTX 3080 Ti)','VRAM']:
            v=box(True,4)
            row,val=row_pair(title,'—')
            v.pack_start(row,False,False,0)
            prog=Gtk.ProgressBar()
            prog.get_style_context().add_class('progress')
            prog.set_fraction(0)
            v.pack_start(prog,False,False,0)
            content.pack_start(v,False,False,0)
            self.progress.append((val,prog))
        b=button('↻ Update GPU',self.refresh_gpu, 'Queries NVIDIA only when clicked')
        b.get_style_context().add_class('snapshot-button')
        content.pack_start(b,False,False,0)
        column.pack_start(card(content,540,290),False,False,0)

    def refresh_resources(self):
        cpu=psutil.cpu_percent(None)
        mem=psutil.virtual_memory()
        self.progress[0][0].set_text(f'{cpu:.0f}%')
        self.progress[0][1].set_fraction(min(cpu/100,1))
        self.progress[1][0].set_text(f'{mem.used/2**30:.1f} / {mem.total/2**30:.0f} GiB ({mem.percent:.0f}%)')
        self.progress[1][1].set_fraction(mem.percent/100)
        return True

    def refresh_gpu(self):
        txt=run('nvidia-smi','--query-gpu=utilization.gpu,temperature.gpu,memory.used,memory.total','--format=csv,noheader,nounits')
        try:
            util,temp,used,total=[float(x.strip()) for x in txt.split(',')[:4]]
            self.progress[2][0].set_text(f'{util:.0f}% ({temp:.0f}°C)')
            self.progress[2][1].set_fraction(min(util/100,1))
            self.progress[3][0].set_text(f'{used/1024:.1f}/{total/1024:.1f} GiB')
            self.progress[3][1].set_fraction(min(used/total,1))
        except (ValueError,ZeroDivisionError):
            self.progress[2][0].set_text('NVIDIA unavailable')

    def setup_music(self, column):
        content=box(True,10)
        row=box(False,16)
        self.cover=(Gtk.Image.new_from_file(str(ASSETS/'album-fallback.png'))
                    if (ASSETS/'album-fallback.png').is_file()
                    else Gtk.Image.new_from_icon_name('audio-x-generic', Gtk.IconSize.DIALOG))
        self.cover.set_pixel_size(105)
        self.cover_url=''
        cover=self.cover
        row.pack_start(cover,False,False,0)
        details=box(True,7)
        details.pack_start(label('♫  Now Playing','muted'),False,False,0)
        self.song=label('No media playing','music-title')
        self.artist=label('Start a player for MPRIS controls','small')
        self.song.set_single_line_mode(True)
        self.song.set_ellipsize(Pango.EllipsizeMode.END)
        self.song.set_max_width_chars(28)
        self.artist.set_ellipsize(Pango.EllipsizeMode.END)
        self.artist.set_max_width_chars(32)
        details.pack_start(self.song,False,False,0)
        details.pack_start(self.artist,False,False,0)
        row.pack_start(details,True,True,0)
        content.pack_start(row,False,False,0)
        self.musicbar=Gtk.ProgressBar()
        self.musicbar.get_style_context().add_class('progress')
        content.pack_start(self.musicbar,False,False,0)
        ctl=box(False,10)
        for name,cmd,tip in [('⤨','shuffle','Shuffle'),('⏮','previous','Previous'),('⏯','play-pause','Play/Pause'),('⏭','next','Next'),('↻','loop','Toggle repeat')]:
            b=button(name,lambda c=cmd:self.player_action(c),tip)
            if cmd == 'play-pause':
                b.get_style_context().add_class('media-primary')
            ctl.pack_start(b,True,True,0)
        content.pack_start(ctl,False,False,0)
        self.player_state=label('Real MPRIS player state · no simulated tracks','small')
        content.pack_start(self.player_state,False,False,0)
        column.pack_start(card(content,540,270),False,False,0)

    def player_action(self,cmd):
        target=getattr(self,'music_player',None)
        argv=['playerctl']+(['-p',target] if target else [])+[cmd]
        subprocess.Popen(argv,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL) if GLib.find_program_in_path('playerctl') else None
        GLib.timeout_add(500,lambda: (self.refresh_music(), False)[1])

    def refresh_music(self):
        spotify_status=run('playerctl','-p','spotify','status')
        self.music_player='spotify' if spotify_status in ('Playing','Paused') else None
        cmd=['playerctl']+(['-p',self.music_player] if self.music_player else [])
        status=run(*cmd,'status')
        if status not in ('Playing','Paused'):
            self.song.set_text('No media playing')
            self.artist.set_text('Chrome, Spotify, VLC, etc.')
            self.player_state.set_text('Connect a media player to activate controls')
            self.musicbar.set_fraction(0)
            if self.cover_url:
                self.cover_url=''
                self.cover.set_from_file(str(ASSETS/'album-fallback.png')) if (ASSETS/'album-fallback.png').is_file() else self.cover.set_from_icon_name('audio-x-generic', Gtk.IconSize.DIALOG)
            return True
        meta=run(*cmd,'metadata','--format','{{title}}\n{{artist}}')
        parts=meta.splitlines()
        full_title = parts[0] if parts else 'Untitled'
        full_artist = parts[1] if len(parts)>1 else 'Unknown artist'
        self.song.set_text(full_title)
        self.song.set_tooltip_text(full_title)
        self.artist.set_text(full_artist)
        self.artist.set_tooltip_text(full_artist)
        self.player_state.set_text(status+' · MPRIS')
        self.refresh_cover()
        duration=run(*cmd,'metadata','--format','{{mpris:length}}')
        pos=run(*cmd,'position')
        try:
            self.musicbar.set_fraction(min(max(float(pos)/(float(duration)/1e6),0),1))
        except (ZeroDivisionError,ValueError): self.musicbar.set_fraction(0)
        return True

    def refresh_cover(self):
        # Fetch cover ONLY when the real player's MPRIS URL changes.
        cmd=['playerctl']+(['-p',self.music_player] if getattr(self,'music_player',None) else [])
        url=run(*cmd,'metadata','--format','{{mpris:artUrl}}')
        if url==self.cover_url:
            return
        self.cover_url=url
        # Never keep artwork from a previous track when a new source fails.
        self.cover.set_from_file(str(ASSETS/'album-fallback.png')) if (ASSETS/'album-fallback.png').is_file() else self.cover.set_from_icon_name('audio-x-generic', Gtk.IconSize.DIALOG)
        if not url:
            return
        def fetch():
            try:
                parsed=urllib.parse.urlsplit(url)
                if parsed.scheme=='https' and parsed.hostname in ('i.scdn.co','mosaic.scdn.co','image-cdn.spotifycdn.com'):
                    class NoRedirect(urllib.request.HTTPRedirectHandler):
                        def redirect_request(self,*args,**kwargs): return None
                    request=urllib.request.Request(url,headers={'User-Agent':'ShioriCrimson/3.3'})
                    with urllib.request.build_opener(NoRedirect()).open(request, timeout=4) as res:
                        data=res.read(2_000_001)
                elif parsed.scheme=='file':
                    path=Path(urllib.request.url2pathname(parsed.path)).resolve()
                    roots=[Path.home()/'.cache',Path('/tmp'),Path(os.environ.get('XDG_RUNTIME_DIR','/run/user/0'))]
                    if not any(path.is_relative_to(root.resolve()) for root in roots): return
                    if path.stat().st_size>2_000_000: return
                    data=path.read_bytes()
                else:
                    return
                if len(data)>2_000_000: return
                loader=GdkPixbuf.PixbufLoader()
                loader.write(data)
                loader.close()
                pix=loader.get_pixbuf()
                if pix is None: return
                scaled=pix.scale_simple(105,105,GdkPixbuf.InterpType.BILINEAR)
                def display():
                    if self.cover_url==url:
                        self.cover.set_from_pixbuf(scaled)
                    return False
                GLib.idle_add(display)
            except (OSError,ValueError,GLib.Error,urllib.error.URLError):
                return
        threading.Thread(target=fetch,daemon=True,name='shiori-mpris-cover').start()

    def setup_clock(self, column):
        content=box(True,15)
        self.clock=label('00:00','bigclock')
        self.date=label('','clock-date')
        content.pack_start(self.clock,False,False,0)
        content.pack_start(self.date,False,False,0)
        separator=Gtk.Separator()
        content.pack_start(separator,False,False,12)
        quote=label('“Coding... with you by my side,\nthat’s my kind of eternity.”','quote')
        quote.set_line_wrap(True)
        content.pack_start(quote,False,False,0)
        content.pack_start(label('— Shiori ♡','muted'),False,False,0)
        column.pack_start(card(content,540,320),False,False,0)

    def refresh_clock(self):
        now=datetime.datetime.now().astimezone()
        self.clock.set_text(now.strftime('%H:%M'))
        self.date.set_text(now.strftime('%a, %b %d, %Y'))
        return True

    def setup_launcher(self):
        # No layer-shell anchors means truly centered on the LG output.
        # Overlay layer puts the modal above the dashboard and Waybar.
        self.launcher=window('launcher', self.lg, 744, 702,
                layer=GtkLayerShell.Layer.OVERLAY, keyboard=True)
        GtkLayerShell.set_keyboard_mode(self.launcher, GtkLayerShell.KeyboardMode.EXCLUSIVE)
        content=box(True, 12)
        content.get_style_context().add_class('launcher-shell')
        content.set_size_request(744,702)

        hero=box(False, 17)
        hero.get_style_context().add_class('launcher-hero')
        herocopy=box(True, 6)
        herocopy.pack_start(label('✦  THE CRIMSON GATEWAY', 'launcher-kicker'),False,False,0)
        herocopy.pack_start(label('SHIORI  //  ASURA', 'launcher-brand'),False,False,0)
        herocopy.pack_start(label('Your applications, beneath the crimson moon.', 'launcher-subtitle'),False,False,0)
        herocopy.pack_start(label('⛩  HYPRLAND     •     UBUNTU 26.04', 'launcher-tag'),False,False,0)
        hero.pack_start(herocopy,True,True,0)
        imagefile=ASSETS/'shiori-menu-portrait.png'
        if imagefile.is_file():
            try:
                pix=GdkPixbuf.Pixbuf.new_from_file_at_scale(str(imagefile), 93, 140, True)
                portrait=Gtk.Image.new_from_pixbuf(pix)
                portrait.get_style_context().add_class('launcher-art')
                hero.pack_end(portrait,False,False,0)
            except GLib.Error:
                pass
        content.pack_start(hero,False,False,0)

        search=Gtk.Entry()
        search.set_placeholder_text('⌕  Search installed applications...')
        search.get_style_context().add_class('launcher-search')
        search.connect('changed',self.on_search)
        search.connect('key-press-event',self.on_search_key)
        content.pack_start(search,False,False,0)
        self.search=search
        self.apps=self.find_apps()

        heading=box(False, 12)
        heading.pack_start(label('QUICK ACCESS','launcher-section'),False,False,0)
        heading.pack_end(label('PINNED TO ASURA', 'launcher-hint'),False,False,0)
        content.pack_start(heading,False,False,0)

        quick=Gtk.Grid()
        quick.set_column_spacing(8)
        buttons=[('Chrome','chrome','web-browser',('google chrome','google-chrome')),
                 ('VS Code','code','text-editor',('visual studio code','code - oss','vscodium')),
                 ('Discord','discord','internet-chat',('discord',)),
                 ('Spotify','spotify','multimedia-player',('spotify',)),
                 ('Terminal','kitty','utilities-terminal',('kitty',)),
                 ('Files','nautilus','system-file-manager',('files','nautilus'))]
        for col,(name,action,icon_name,aliases) in enumerate(buttons):
            b=Gtk.Button()
            b.get_style_context().add_class('launcher-pin')
            inner=box(True,4)
            match=next((a for a in self.apps if any(k in (a.get_name()+' '+(a.get_executable() or '')).lower() for k in aliases)),None)
            gicon=match.get_icon() if match else None
            if gicon:
                symbol=Gtk.Image.new_from_gicon(gicon,Gtk.IconSize.DND)
            else:
                # Only use the host's icon theme. Never bundle third-party brand PNGs.
                symbol=Gtk.Image.new_from_icon_name(icon_name,Gtk.IconSize.DND)
            inner.pack_start(symbol,False,False,0)
            text=label(name,'launcher-pin-label',.5)
            inner.pack_start(text,False,False,0)
            b.add(inner)
            b.connect('clicked',lambda _, a=action:self.open_pinned(a))
            quick.attach(b,col,0,1,1)
        content.pack_start(quick,False,False,0)

        heading2=box(False,12)
        self.app_count=label('ALL APPLICATIONS','launcher-section')
        heading2.pack_start(self.app_count,False,False,0)
        settings_button=Gtk.Button()
        settings_button.get_style_context().add_class('launcher-pin')
        settings_button.add(label('⚙  SYSTEM SETTINGS','launcher-pin-label'))
        settings_button.connect('clicked',lambda *_:self.open_settings())
        heading2.pack_end(settings_button,False,False,0)
        content.pack_start(heading2,False,False,0)
        self.rows=box(True,3)
        scroll=Gtk.ScrolledWindow()
        scroll.get_style_context().add_class('launcher-results')
        scroll.set_policy(Gtk.PolicyType.NEVER,Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.rows)
        scroll.set_min_content_height(180)
        content.pack_start(scroll,True,True,0)
        foot=box(False,10)
        foot.pack_start(label('ESC to close  ·  ENTER to launch  ·  Super+D to toggle','launcher-footer'),True,True,0)
        foot.pack_end(label('SHIORI CRIMSON  ♡','launcher-kicker'),False,False,0)
        content.pack_start(foot,False,False,0)
        self.launcher.add(content)
        self.update_apps('')
        self.windows.append(self.launcher)

    def open_pinned(self,action):
        # Reuse the existing, tested launch.sh actions (including Wayland flags).
        try:
            subprocess.Popen([str(HOME/'.config/shiori-v3/launch.sh'),action],
                             stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,start_new_session=True)
        except OSError as err:
            print('Shiori pinned launcher failed',action,err,file=sys.stderr)
        self.launcher.hide()

    def find_apps(self):
        # Gio.AppInfo.get_all includes desktop entries excluded by OnlyShowIn.
        # Filter Hidden/NoDisplay, but keep GNOME Settings under Hyprland.
        return shiori_discover_apps(Gio.AppInfo.get_all())

    def update_apps(self,query):
        for child in self.rows.get_children():
            self.rows.remove(child)
        self.visible_apps=[]
        matches=shiori_search_apps(self.apps,query)
        self.app_count.set_text(f'ALL APPLICATIONS  ·  {len(matches)}/{len(self.apps)}')
        for app in matches:
            r=Gtk.Button()
            r.get_style_context().add_class('launch-row')
            h=box(False,14)
            ico=app.get_icon()
            icon=Gtk.Image.new_from_gicon(ico,Gtk.IconSize.DND) if ico else Gtk.Image.new_from_icon_name('application-x-executable',Gtk.IconSize.DND)
            h.pack_start(icon,False,False,0)
            details=box(True,3)
            details.pack_start(label(app.get_name(),'launch-name'),False,False,0)
            exe=(app.get_executable() or 'Application').split('/')[-1]
            details.pack_start(label(exe,'launch-desc'),False,False,0)
            h.pack_start(details,True,True,0)
            h.pack_end(label('›','launch-arrow'),False,False,0)
            r.add(h)
            r.connect('clicked',lambda _,a=app:self.open_app(a))
            self.rows.pack_start(r,False,False,0)
            self.visible_apps.append(app)
        if not matches:
            self.rows.pack_start(label('No matching applications. Try a different search.','launch-desc'),False,False,18)
        self.rows.show_all()

    def open_settings(self):
        # GNOME Control Center refuses to start outside GNOME/Unity unless
        # XDG_CURRENT_DESKTOP includes GNOME. Change the child only: Hyprland,
        # portals, Flatpak and the global session environment remain untouched.
        import shutil
        executable = shutil.which('gnome-control-center')
        if not executable:
            print('Shiori Settings: gnome-control-center not installed', file=sys.stderr)
            self.app_count.set_text('SYSTEM SETTINGS NOT INSTALLED')
            return
        env = os.environ.copy()
        env['XDG_CURRENT_DESKTOP'] = 'GNOME'
        log_file = HOME / '.cache/shiori-v3.3.3.1-settings.log'
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with log_file.open('a', encoding='utf-8') as output:
                output.write('Shiori: starting GNOME Settings in a GNOME-scoped child environment\n')
                output.flush()
                subprocess.Popen([executable], env=env, stdin=subprocess.DEVNULL,
                                 stdout=output, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        except OSError as err:
            print('Shiori Settings: failed launching GNOME Control Center:', err, file=sys.stderr)
            self.app_count.set_text('SETTINGS FAILED · CHECK HUD LOG')
            return
        self.launcher.hide()

    def open_app(self,app):
        if shiori_is_settings(app):
            self.open_settings()
            return
        name=(app.get_name()+' '+(app.get_executable() or '')).lower()
        routes=[('discord','discord'),('spotify','spotify'),('visual studio code','code'),
                ('code - oss','code'),('vscodium','code'),('google chrome','chrome'),
                ('google-chrome','chrome'),('docker desktop','docker')]
        command=next((route for term,route in routes if term in name),None)
        try:
            if command:
                subprocess.Popen([str(HOME/'.config/shiori-v3/launch.sh'),command],
                                 stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL,start_new_session=True)
            else:
                app.launch([],None)
        except (GLib.Error,OSError) as err:
            print('Cannot launch',app.get_name(),err,file=sys.stderr)
        self.launcher.hide()

    def on_search(self,entry): self.update_apps(entry.get_text())

    def on_search_key(self,entry,event):
        if event.keyval==Gdk.KEY_Escape: self.launcher.hide(); return True
        if event.keyval in (Gdk.KEY_Return,Gdk.KEY_KP_Enter) and self.visible_apps:
            self.open_app(self.visible_apps[0]);return True
        return False

    def toggle(self,force=None):
        if force=='hide' or (force is None and self.launcher.get_visible()):
            self.launcher.hide()
        else:
            # Pick up newly installed Flatpak, Snap and native desktop entries
            # every time the launcher opens; no Hyprland logout necessary.
            self.apps=self.find_apps()
            if self.search.get_text():
                self.search.set_text('')  # emits changed, triggers update_apps
            else:
                self.update_apps('')
            self.launcher.show_all()
            self.search.grab_focus()

    def make_socket(self):
        if SOCKET.exists():
            if send('status')==0:
                sys.exit('Shiori HUD already running')
            SOCKET.unlink()
        self.sock=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        self.sock.bind(str(SOCKET))
        os.chmod(SOCKET,0o600)
        self.sock.listen(5)
        self.sock.setblocking(False)
        GLib.io_add_watch(self.sock.fileno(),GLib.IO_IN,self.socket_ready)

    def socket_ready(self,_,cond):
        try:
            conn,_=self.sock.accept()
            with conn: msg=conn.recv(128).decode('utf8').strip()
        except BlockingIOError: return True
        if msg=='toggle': self.toggle()
        elif msg=='show': self.toggle('show')
        elif msg=='hide': self.toggle('hide')
        elif msg=='stop': Gtk.main_quit()
        elif msg=='gpu': self.refresh_gpu()
        return True

    def cleanup(self):
        self.sock.close()
        try: SOCKET.unlink()
        except FileNotFoundError: pass

if __name__=='__main__':
    h=ShioriHud()
    try: Gtk.main()
    finally: h.cleanup()
