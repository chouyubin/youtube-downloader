"""YouTube Downloader GUI with i18n"""
import os, sys, io, threading, time
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox
if sys.platform == "win32" and sys.stdout:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from downloader import YouTubeDownloader, check_ffmpeg, check_aria2
from torrent_maker import TorrentMaker
from i18n import I18n, load_lang
from themes import get_theme, list_themes, load_theme, save_theme

C = get_theme(load_theme())

def apply_theme(name: str):
    global C
    C = get_theme(name)
    save_theme(name)

def setup_styles():
    s = ttk.Style(); s.theme_use("clam")
    s.configure("TProgressbar", background=C.get("green","#3fb950"), troughcolor=C.get("bg3","#21262d"), borderwidth=0, thickness=10)
    s.configure("TScrollbar", background=C.get("bg3","#21262d"), troughcolor=C.get("bg","#0d1117"), borderwidth=0, arrowcolor=C.get("fg2","#8b949e"))

def card(p): return Frame(p, bg=C["bg2"], highlightbackground=C["border"], highlightthickness=1)
def slbl(p, t): return Label(p, text=t, fg=C["fg"], bg=C["bg2"], font=("Microsoft YaHei", 11, "bold"), anchor=W)
def sbtn(p, t, cmd, clr=None, fs=10, bd=True, padx=14, pady=5, **kw):
    c = clr or C["accent"]
    btn = Button(p, text=t, command=cmd, bg=c,
        fg="#fff" if c != C["bg3"] else C["fg"],
        font=("Microsoft YaHei", fs, "bold" if bd else "normal"),
        relief=FLAT, cursor="hand2", bd=0, padx=padx, pady=pady,
        activebackground=c, activeforeground="white", **kw)
    btn.bind("<Enter>", lambda e: btn.configure(relief=RAISED))
    btn.bind("<Leave>", lambda e: btn.configure(relief=FLAT))
    return btn




class ToolTip:
    """悬浮提示框"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tw = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, e):
        if self.tw: return
        x = self.widget.winfo_rootx() + self.widget.winfo_width() + 6
        y = self.widget.winfo_rooty()
        self.tw = Toplevel(self.widget)
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry(f"+{x}+{y}")
        self.tw.configure(bg=C["bg2"], highlightbackground=C["yellow"], highlightthickness=1)
        label = Label(self.tw, text=self.text, justify=LEFT,
            bg=C["bg2"], fg=C["fg"], font=("Microsoft YaHei", 9),
            relief=SOLID, borderwidth=1, padx=10, pady=6,
            wraplength=320)
        label.pack()

    def _hide(self, e):
        if self.tw:
            self.tw.destroy()
            self.tw = None


def help_icon(parent, text):
    """创建 ? 帮助图标"""
    lbl = Label(parent, text=" ? ", bg=C["bg2"], fg=C["fg2"],
        font=("Microsoft YaHei", 8, "bold"), cursor="question_arrow")
    ToolTip(lbl, text)
    return lbl

class SettingsDialog:
    def __init__(self, parent, app):
        self.app = app
        self.T = app.i18n.t
        self.w = Toplevel(parent)
        self.w.title(self.T("settings_title"))
        self.w.geometry("480x580")
        self.w.resizable(False, False)
        self.w.configure(bg=C["bg"])
        self.w.transient(parent); self.w.grab_set()
        self._build()
        x = parent.winfo_rootx() + (parent.winfo_width() - 480) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 580) // 2
        self.w.geometry(f"+{x}+{y}")

    def _build(self):
        T = self.T
        # Scrollable container
        canvas = Canvas(self.w, bg=C["bg"], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.w, orient="vertical", command=canvas.yview)
        m = Frame(canvas, bg=C["bg"])
        m.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=m, anchor="nw", width=448)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.w.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

        Label(m, text=T("settings_title"), fg=C["fg"], bg=C["bg"],
            font=("Microsoft YaHei", 16, "bold")).pack(anchor=W, padx=16, pady=(16,12))

        # Theme
        ct = card(m); ct.pack(fill=X, pady=(0,10))
        slbl(ct, "Theme").pack(anchor=W, padx=12, pady=(10,4))
        tf = Frame(ct, bg=C["bg2"]); tf.pack(fill=X, padx=12, pady=(0,10))
        themes_list = list_themes()
        cur_theme = load_theme()
        for i, (key, name) in enumerate(themes_list):
            if i > 0 and i % 2 == 0:
                # new row every 2 buttons
                pass
            color = C["green"] if cur_theme == key else C["bg3"]
            fgc = "#fff" if cur_theme == key else C["fg2"]
            btn = Button(tf, text=name, bg=color, fg=fgc,
                font=("Microsoft YaHei", 8, "bold" if cur_theme == key else "normal"),
                relief=FLAT, cursor="hand2", bd=0, padx=8, pady=4,
                activebackground=C["green"], activeforeground="white")
            btn.configure(command=lambda k=key: [apply_theme(k), self.app._rebuild_ui(), self.w.destroy()])
            btn.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
        for col in range(2): tf.grid_columnconfigure(col, weight=1, uniform="th")

        # Language
        c0 = card(m); c0.pack(fill=X, pady=(0,10))
        slbl(c0, T("language")).pack(anchor=W, padx=12, pady=(10,4))
        lf = Frame(c0, bg=C["bg2"]); lf.pack(fill=X, padx=12, pady=(0,10))
        for lang, label in [("zh", "\u4e2d\u6587"), ("en", "English")]:
            color = C["green"] if self.app.i18n.lang == lang else C["bg3"]
            fg_color = "#fff" if self.app.i18n.lang == lang else C["fg2"]
            Button(lf, text=label, command=lambda l=lang: self._switch_lang(l),
                bg=color, fg=fg_color, font=("Microsoft YaHei", 10, "bold"),
                relief=FLAT, cursor="hand2", bd=0, padx=16, pady=6,
                activebackground=C["green"], activeforeground="white").pack(side=LEFT, padx=(0,8))

        # Proxy
        c1 = card(m); c1.pack(fill=X, pady=(0,10))
        slbl(c1, T("proxy")).pack(anchor=W, padx=12, pady=(10,4))
        pf = Frame(c1, bg=C["bg2"]); pf.pack(fill=X, padx=12, pady=(0,10))
        Entry(pf, textvariable=self.app.proxy_var, bg=C["bg3"], fg=C["fg"],
            font=("Consolas", 9), relief=FLAT, bd=0).pack(side=LEFT, fill=X, expand=True, ipady=6)
        Button(pf, text=T("test_proxy"), command=self._tp, bg=C["blue"], fg="white",
            font=("Microsoft YaHei", 8), relief=FLAT, cursor="hand2", bd=0, padx=12,
            activebackground=C["blue"]).pack(side=LEFT, padx=(6,0))

        # Cookies
        ck = card(m); ck.pack(fill=X, pady=(0,10))
        slbl(ck, T("cookies")).pack(anchor=W, padx=12, pady=(10,4))
        ckf = Frame(ck, bg=C["bg2"]); ckf.pack(fill=X, padx=12, pady=(0,6))
        browsers = [("chrome", "Chrome"), ("firefox", "Firefox"), ("edge", "Edge"), ("brave", "Brave"), ("opera", "Opera")]
        for i, (bkey, bname) in enumerate(browsers):
            color = C["green"] if self.app.cookies_var.get() == bkey else C["bg3"]
            fg_color = "#fff" if self.app.cookies_var.get() == bkey else C["fg2"]
            Button(ckf, text=bname, bg=color, fg=fg_color,
                font=("Microsoft YaHei", 8, "bold" if self.app.cookies_var.get() == bkey else "normal"),
                relief=FLAT, cursor="hand2", bd=0, padx=8, pady=3,
                activebackground=C["green"], activeforeground="white",
                command=lambda k=bkey: [self.app.cookies_var.set(k), self._refresh_cookies_btns(ckf)]).grid(row=0, column=i, padx=2)
        for col in range(5): ckf.grid_columnconfigure(col, weight=1)
        # Hint text
        Label(ck, text=T("cookies_hint"), fg=C["fg2"], bg=C["bg2"],
            font=("Microsoft YaHei", 7), anchor="w", justify=LEFT).pack(fill=X, padx=12, pady=(0,8))

        # Download
        c2 = card(m); c2.pack(fill=X, pady=(0,10))
        slbl(c2, T("download_settings")).pack(anchor=W, padx=12, pady=(10,4))
        df = Frame(c2, bg=C["bg2"]); df.pack(fill=X, padx=12, pady=(0,6))
        Label(df, text=T("default_quality"), fg=C["fg2"], bg=C["bg2"], font=("Microsoft YaHei",9)).grid(row=0,column=0,sticky=W)
        qm = OptionMenu(df, self.app.quality_var, "best","4k","1440p","1080p","720p","480p","360p")
        qm.configure(bg=C["bg3"], fg=C["fg"], font=("Consolas",9), relief=FLAT, bd=0, highlightthickness=0, indicatoron=0, padx=6)
        qm["menu"].configure(bg=C["bg3"], fg=C["fg"], font=("Consolas",9), relief=FLAT)
        qm.grid(row=0, column=1, sticky=W, padx=(8,16))
        Label(df, text=T("default_format"), fg=C["fg2"], bg=C["bg2"], font=("Microsoft YaHei",9)).grid(row=0,column=2,sticky=W)
        fm = OptionMenu(df, self.app.format_var, "mp4","mkv","webm")
        fm.configure(bg=C["bg3"], fg=C["fg"], font=("Consolas",9), relief=FLAT, bd=0, highlightthickness=0, indicatoron=0, padx=6)
        fm["menu"].configure(bg=C["bg3"], fg=C["fg"], font=("Consolas",9), relief=FLAT)
        fm.grid(row=0, column=3, sticky=W, padx=(8,0))

        tf = Frame(c2, bg=C["bg2"]); tf.pack(fill=X, padx=12, pady=(0,6))
        Label(tf, text=T("threads"), fg=C["fg2"], bg=C["bg2"], font=("Microsoft YaHei",9)).pack(side=LEFT)
        Button(tf, text="-", command=lambda: self.app.threads_var.set(max(1,self.app.threads_var.get()-1)),
            bg=C["bg3"], fg=C["fg"], font=("Consolas",11), relief=FLAT, bd=0, padx=10, cursor="hand2").pack(side=LEFT, padx=(8,0))
        Label(tf, textvariable=self.app.threads_var, bg=C["bg3"], fg=C["cyan"],
            font=("Consolas",12,"bold"), width=3).pack(side=LEFT)
        Button(tf, text="+", command=lambda: self.app.threads_var.set(min(16,self.app.threads_var.get()+1)),
            bg=C["bg3"], fg=C["fg"], font=("Consolas",11), relief=FLAT, bd=0, padx=10, cursor="hand2").pack(side=LEFT)

        cf = Frame(c2, bg=C["bg2"]); cf.pack(fill=X, padx=12, pady=(0,6))
        Checkbutton(cf, text=T("use_aria2"), variable=self.app.use_aria2_var,
            bg=C["bg2"], fg=C["fg"], selectcolor=C["bg3"], activebackground=C["bg2"],
            activeforeground=C["fg"], font=("Microsoft YaHei",9), relief=FLAT, bd=0, cursor="hand2").pack(side=LEFT)
        if not self.app.has_aria2:
            Label(cf, text=T("aria2_missing"), fg=C["fg2"], bg=C["bg2"], font=("Microsoft YaHei",8)).pack(side=LEFT, padx=(2,16))
        Checkbutton(cf, text=T("force_ipv4"), variable=self.app.force_ipv4_var,
            bg=C["bg2"], fg=C["fg"], selectcolor=C["bg3"], activebackground=C["bg2"],
            activeforeground=C["fg"], font=("Microsoft YaHei",9), relief=FLAT, bd=0, cursor="hand2").pack(side=LEFT, padx=(16,0))

        # GPU (auto-select encoder)
        if self.app.downloader.gpu_info["type"]:
            gpf = Frame(c2, bg=C["bg2"]); gpf.pack(fill=X, padx=12, pady=(0,6))
            Label(gpf, text=T("gpu_accel"), fg=C["fg2"], bg=C["bg2"], font=("Microsoft YaHei",9)).pack(side=LEFT)
            gpu_name = self.app.downloader.gpu_info["type"].upper()
            gpu_full = self.app.downloader.gpu_info["name"][:30]
            Checkbutton(gpf, text=f"{gpu_name} ({gpu_full}) - auto h264/hevc",
                variable=self.app.gpu_enabled_var, bg=C["bg2"], fg=C["purple"],
                selectcolor=C["bg3"], activebackground=C["bg2"], activeforeground=C["purple"],
                font=("Microsoft YaHei",9), relief=FLAT, bd=0, cursor="hand2").pack(side=LEFT, padx=(8,0))

        # Output
        c3 = card(m); c3.pack(fill=X, pady=(0,12))
        slbl(c3, T("output_dir")).pack(anchor=W, padx=12, pady=(10,4))
        of = Frame(c3, bg=C["bg2"]); of.pack(fill=X, padx=12, pady=(0,10))
        Entry(of, textvariable=self.app.output_dir_var, bg=C["bg3"], fg=C["fg"],
            font=("Consolas",9), relief=FLAT, bd=0, state="readonly",
            readonlybackground=C["bg3"]).pack(side=LEFT, fill=X, expand=True, ipady=6)
        Button(of, text=T("browse"), command=self.app._on_browse_dir, bg=C["bg3"], fg=C["fg"],
            font=("Microsoft YaHei",9), relief=FLAT, cursor="hand2", bd=0, padx=10,
            activebackground=C["accent"]).pack(side=LEFT, padx=(6,0))

        bf = Frame(m, bg=C["bg"]); bf.pack(fill=X)
        sbtn(bf, T("reset"), self._rs, C["bg3"], fs=9).pack(side=LEFT)
        sbtn(bf, T("save"), self._sv, C["green"], fs=10).pack(side=RIGHT)

    def _switch_lang(self, lang):
        self.app.i18n.switch(lang)
        self.w.destroy()
        self.app._rebuild_ui()

    def _refresh_cookies_btns(self, parent):
        for child in parent.winfo_children():
            if isinstance(child, Button):
                browser_map = {"Chrome": "chrome", "Firefox": "firefox", "Edge": "edge", "Brave": "brave", "Opera": "opera"}
                name = child.cget("text")
                if name in browser_map:
                    key = browser_map[name]
                    is_sel = self.app.cookies_var.get() == key
                    child.configure(bg=C["green"] if is_sel else C["bg3"],
                        fg="#fff" if is_sel else C["fg2"],
                        font=("Microsoft YaHei", 8, "bold" if is_sel else "normal"))

    def _tp(self):
        px = self.app.proxy_var.get().strip()
        if not px: messagebox.showinfo("Info", self.T("test_enter")); return
        try:
            import urllib.request
            urllib.request.build_opener(urllib.request.ProxyHandler({"http":px,"https":px})).open("https://www.google.com", timeout=5)
            messagebox.showinfo("OK", self.T("test_ok"))
        except Exception as e:
            messagebox.showwarning("Fail", f"{self.T('test_fail')}:\n{str(e)[:120]}")

    def _rs(self):
        self.app.proxy_var.set("")
        self.app.quality_var.set("best"); self.app.format_var.set("mp4")
        self.app.threads_var.set(8); self.app.use_aria2_var.set(False)
        self.app.force_ipv4_var.set(True)
        self.app.gpu_enabled_var.set(False)
        self.app.output_dir_var.set(str(Path.home()/"Downloads"/"YouTube"))
        self.app.cookies_var.set("")
        messagebox.showinfo("OK", self.T("reset_done"))

    def _sv(self):
        self.app.downloader.set_proxy(self.app.proxy_var.get())
        self.app.downloader.output_dir = self.app.output_dir_var.get()
        self.app.downloader.set_options(
            multi_thread=self.app.multi_thread_var.get(),
            threads=self.app.threads_var.get(),
            use_aria2=self.app.use_aria2_var.get(),
            force_ipv4=self.app.force_ipv4_var.get(),
        )
        cookie_val = self.app.cookies_var.get().strip()
        self.app.downloader.cookies_from_browser = ""
        self.app.downloader.cookies_file = ""
        if cookie_val:
            if cookie_val in ("chrome", "firefox", "edge", "brave", "opera"):
                self.app.downloader.cookies_from_browser = cookie_val
            else:
                self.app.downloader.cookies_file = cookie_val
        messagebox.showinfo("OK", self.T("saved"))
        self.w.destroy()


class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.i18n = I18n()
        self._t = self.i18n.t  # shortcut

        self.root.title(self._t("app_title"))
        self.root.geometry("700x680")
        self.root.minsize(560, 600)
        self.root.configure(bg=C["bg"])

        self.downloader = YouTubeDownloader()
        self.torrent_maker = TorrentMaker()
        self.downloading = False
        self.current_file = None

        # Vars
        self.url_var = StringVar()
        self.quality_var = StringVar(value="best")
        self.format_var = StringVar(value="mp4")
        self.audio_only_var = BooleanVar(value=False)
        self.subtitle_var = BooleanVar(value=False)
        self.sub_lang_var = StringVar(value="zh-Hans,en")
        self.playlist_var = BooleanVar(value=False)
        self.make_torrent_var = BooleanVar(value=False)
        self.multi_thread_var = BooleanVar(value=True)
        self.use_aria2_var = BooleanVar(value=False)
        self.force_ipv4_var = BooleanVar(value=True)
        self.threads_var = IntVar(value=8)
        self.output_dir_var = StringVar(value=self.downloader.output_dir)
        self.proxy_var = StringVar(value="")
        self.gpu_enabled_var = BooleanVar(value=False)
        self.console_enabled_var = BooleanVar(value=True)
        self.cookies_var = StringVar(value="")  # chrome, firefox, edge, or file path
        self._console_visible = False
        self.progress_var = DoubleVar(value=0)
        self.status_var = StringVar()

        self.has_ffmpeg = check_ffmpeg()
        self.has_aria2 = check_aria2()

        self._build_ui()
        self._bind_events()
        self._refresh_texts()
        self.i18n.on_change(lambda: self._refresh_texts())

    def _refresh_texts(self):
        """刷新所有 UI 文本"""
        self._t = self.i18n.t
        self.root.title(self._t("app_title"))
        self.status_var.set(self._t("ready"))
        # 按钮文本通过 textvariable 或直接设置在这里由 _rebuild_ui 处理
        # 这里只处理动态 textvariable
        self.status_var.set(self._t("ready"))

    def _rebuild_ui(self):
        """重建 UI（语言/主题切换时调用）"""
        global C
        C = get_theme(load_theme())
        setup_styles()
        for w in self.mf.winfo_children():
            w.destroy()
        self._build_ui()
        self._bind_events()
        self._refresh_texts()

    def _build_ui(self):
        T = self._t
        r = self.root
        r.grid_rowconfigure(0, weight=1); r.grid_columnconfigure(0, weight=1)

        self.canvas = Canvas(r, bg=C["bg"], highlightthickness=0, bd=0)
        scr = ttk.Scrollbar(r, orient="vertical", command=self.canvas.yview)
        self.mf = Frame(self.canvas, bg=C["bg"])
        self.mf.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self._cw = self.canvas.create_window((0,0), window=self.mf, anchor="nw")
        self.canvas.configure(yscrollcommand=scr.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scr.grid(row=0, column=1, sticky="ns")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self._cw, width=e.width))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta/120), "units"))

        mf = self.mf; mf.grid_columnconfigure(0, weight=1)

        # === Header ===
        h = Frame(mf, bg=C["bg"]); h.grid(row=0, column=0, sticky="ew", pady=(4,6)); h.grid_columnconfigure(1, weight=1)
        Label(h, text=T("app_title"), fg=C["fg"], bg=C["bg"],
            font=("Microsoft YaHei", 17, "bold")).grid(row=0, column=0, sticky="w", padx=(12,4))
        # Tool status with download buttons
        col = 1
        # FFmpeg
        ff_ok = "FFmpeg OK" if self.has_ffmpeg else "FFmpeg MISSING"
        ff_color = C["green"] if self.has_ffmpeg else C["red"]
        Label(h, text=ff_ok, fg=ff_color, bg=C["bg"],
            font=("Consolas", 8)).grid(row=0, column=col, sticky="e", padx=(0,2)); col += 1
        if not self.has_ffmpeg:
            btn = Button(h, text="Download", command=lambda: __import__("webbrowser").open("https://ffmpeg.org/download.html"),
                bg=C["red"], fg="white", font=("Consolas", 7, "bold"),
                relief=FLAT, cursor="hand2", bd=0, padx=6, pady=1,
                activebackground=C["accent"], activeforeground="white")
            btn.grid(row=0, column=col, sticky="e", padx=(0,4)); col += 1

        # aria2
        aria_ok = "aria2 OK" if self.has_aria2 else "aria2 MISSING"
        aria_color = C["green"] if self.has_aria2 else C["yellow"]
        Label(h, text=aria_ok, fg=aria_color, bg=C["bg"],
            font=("Consolas", 8)).grid(row=0, column=col, sticky="e", padx=(0,2)); col += 1
        if not self.has_aria2:
            btn2 = Button(h, text="Download", command=lambda: __import__("webbrowser").open("https://github.com/aria2/aria2/releases"),
                bg=C["yellow"], fg="black", font=("Consolas", 7, "bold"),
                relief=FLAT, cursor="hand2", bd=0, padx=6, pady=1,
                activebackground=C["accent"], activeforeground="white")
            btn2.grid(row=0, column=col, sticky="e", padx=(0,4)); col += 1

        # GPU
        gpu = self.downloader.gpu_info
        gpu_text = f"GPU: {gpu['type'].upper()}" if gpu["type"] else "GPU: None"
        gpu_color = C["purple"] if gpu["type"] else C["fg2"]
        Label(h, text=gpu_text, fg=gpu_color, bg=C["bg"],
            font=("Consolas", 8)).grid(row=0, column=col, sticky="e", padx=(0,4)); col += 1
        sbtn(h, T("settings"), self._open_settings, C["bg3"], fs=9, bd=False, padx=10, pady=3).grid(row=0, column=col, padx=(0,4)); col += 1

        # Language quick switch
        cur_lang = self.i18n.lang
        lang_icon = "\u4e2d" if cur_lang == "zh" else "EN"
        other_lang = "en" if cur_lang == "zh" else "zh"
        btn_lang = Button(h, text=lang_icon, command=lambda: self._switch_language(other_lang),
            bg=C["bg3"], fg=C["cyan"], font=("Microsoft YaHei", 8, "bold"),
            relief=FLAT, cursor="hand2", bd=0, padx=8, pady=3,
            activebackground=C["accent"], activeforeground="white")
        btn_lang.grid(row=0, column=col, padx=(0,4))
        self._lang_btn = btn_lang

        # === URL ===
        c1 = card(mf); c1.grid(row=1, column=0, sticky="ew", pady=(0,6)); c1.grid_columnconfigure(0, weight=1)
        slbl(c1, T("video_url")).grid(row=0, column=0, sticky="w", padx=12, pady=(10,4))
        uf = Frame(c1, bg=C["bg2"]); uf.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,10)); uf.grid_columnconfigure(0, weight=1)
        self.url_entry = Entry(uf, textvariable=self.url_var, bg=C["bg3"], fg=C["fg"],
            insertbackground=C["accent"], font=("Consolas", 10), relief=FLAT, bd=0)
        self.url_entry.grid(row=0, column=0, sticky="ew", ipady=8)
        sbtn(uf, T("parse"), self._on_parse, C["accent"], fs=10, padx=18).grid(row=0, column=1, padx=(6,0))

        # === Info (hidden) ===
        self.info_frame = Frame(mf, bg=C["bg"])

        # === Options ===
        c2 = card(mf); c2.grid(row=3, column=0, sticky="ew", pady=(0,6))
        hf = Frame(c2, bg=C["bg2"]); hf.pack(fill="x", padx=12, pady=(10,4))
        slbl(hf, T("options")).pack(side=LEFT)
        gpu = self.downloader.gpu_info
        if gpu["type"]:
            gpu_short = gpu["name"].split()[-1] if gpu["name"] else gpu["type"].upper()
            if len(gpu_short) > 15: gpu_short = gpu["type"].upper()
            Checkbutton(hf, text=f"GPU {gpu_short}", variable=self.gpu_enabled_var,
                bg=C["bg2"], fg=C["purple"], selectcolor=C["bg3"], activebackground=C["bg2"],
                activeforeground=C["purple"], font=("Microsoft YaHei", 9, "bold"),
                relief=FLAT, bd=0, cursor="hand2").pack(side=RIGHT, padx=(0,8))
            help_icon(hf, f"硬件加速: {gpu['name']}\n自动选择最佳编码器 (mp4->h264, mkv->hevc)").pack(side=RIGHT, padx=(0,2))
        # Multi-thread with help
        mt_frame = Frame(hf, bg=C["bg2"])
        mt_frame.pack(side=RIGHT)
        Checkbutton(mt_frame, text=T("multi_thread"), variable=self.multi_thread_var,
            bg=C["bg2"], fg=C["cyan"], selectcolor=C["bg3"], activebackground=C["bg2"],
            activeforeground=C["cyan"], font=("Microsoft YaHei", 9, "bold"),
            relief=FLAT, bd=0, cursor="hand2").pack(side=LEFT)
        help_icon(mt_frame, "启用8路并发下载，显著提升下载速度").pack(side=LEFT, padx=(0,8))

        g = Frame(c2, bg=C["bg2"]); g.pack(fill="x", padx=12, pady=(0,10))
        for col in range(4): g.grid_columnconfigure(col, weight=1, uniform="o")
        self._ol(g, T("quality"), 0, 0)
        self._om(g, self.quality_var, ["best","4k","1440p","1080p","720p","480p","360p"], 0, 1)
        self._ol(g, T("format"), 0, 2)
        self._om(g, self.format_var, ["mp4","mkv","webm"], 0, 3)
        self._oc(g, T("audio_only"), self.audio_only_var, 1, 0, 1, help="仅下载音频流并转为 MP3 格式，适合播客/音乐")
        self._oc(g, T("subtitles"), self.subtitle_var, 1, 1, 1, help="下载中英文字幕并嵌入视频文件")
        self._oc(g, T("playlist"), self.playlist_var, 1, 2, 1, help="勾选后下载整个播放列表\n不勾选默认只下载当前单集")
# Single mode is default - see playlist tooltip
        self._oc(g, T("torrent"), self.make_torrent_var, 1, 3, 1, help="下载完成后自动生成 .torrent 种子文件和磁力链接")

        # === Progress ===
        c3 = card(mf); c3.grid(row=4, column=0, sticky="ew", pady=(0,6))
        slbl(c3, T("progress")).pack(anchor="w", padx=12, pady=(10,4))
        self.status_label = Label(c3, textvariable=self.status_var,
            fg=C["accent2"], bg=C["bg2"], font=("Microsoft YaHei", 10, "bold"), anchor="w")
        self.status_label.pack(fill="x", padx=12, pady=(0,6))
        self.pc = Canvas(c3, height=14, bg=C["bg3"], highlightthickness=0, bd=0)
        self.pc.pack(fill="x", padx=12, pady=(0,4))
        self._pb = self.pc.create_rectangle(0,0,0,14, fill=C["green"], outline="")
        self._pt = self.pc.create_text(330,7, text="0%", fill="white", font=("Consolas",8,"bold"))
        self.speed_label = Label(c3, text="", fg=C["fg2"], bg=C["bg2"], font=("Consolas",9), anchor="w")
        self.speed_label.pack(fill="x", padx=12, pady=(0,8))

        # === Log + Console ===
        c4 = card(mf); c4.grid(row=5, column=0, sticky="nsew", pady=(0,6))
        c4.grid_rowconfigure(2, weight=1); c4.grid_columnconfigure(0, weight=1)

        # Toggle bar
        hf2 = Frame(c4, bg=C["bg2"]); hf2.grid(row=0, column=0, sticky="ew", padx=12, pady=(8,2))
        slbl(hf2, T("log")).pack(side=LEFT)

        # Console toggle button
        self._console_btn = Button(hf2, text="Console", command=self._toggle_console,
            bg=C["bg3"], fg=C["cyan"], font=("Microsoft YaHei", 8, "bold"),
            relief=FLAT, cursor="hand2", bd=0, padx=10, pady=2,
            activebackground=C["accent"], activeforeground="white")
        self._console_btn.pack(side=LEFT, padx=(12,0))

        Button(hf2, text=T("clear"), command=self._clear_log, bg=C["bg2"], fg=C["fg2"],
            font=("Microsoft YaHei", 8), relief=FLAT, cursor="hand2", bd=0, padx=8,
            activebackground=C["bg3"]).pack(side=RIGHT)

        # Log panel (default visible)
        self._log_panel = Frame(c4, bg=C["bg2"])
        self._log_panel.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,4))
        self._log_panel.grid_rowconfigure(0, weight=1); self._log_panel.grid_columnconfigure(0, weight=1)
        self.log_text = Text(self._log_panel, bg=C["bg"], fg=C["fg"], font=("Consolas",9),
            relief=FLAT, bd=0, wrap="word", padx=8, pady=6, state=DISABLED)
        self.log_text.grid(row=0, column=0, sticky="nsew")
        ls1 = ttk.Scrollbar(self._log_panel, orient="vertical", command=self.log_text.yview)
        ls1.grid(row=0, column=1, sticky="ns")
        self.log_text.configure(yscrollcommand=ls1.set)
        for tag, color in [("info",C["blue"]),("ok",C["green"]),("err",C["red"]),
            ("warn",C["yellow"]),("time",C["fg2"]),("progress",C["cyan"])]:
            self.log_text.tag_configure(tag, foreground=color)

        # Console panel (hidden by default)
        self._console_panel = Frame(c4, bg=C["bg2"])
        self._console_panel.grid_rowconfigure(0, weight=1); self._console_panel.grid_columnconfigure(0, weight=1)
        self.console_text = Text(self._console_panel, bg=C["bg"], fg=C["cyan"],
            font=("Consolas",9), relief=FLAT, bd=0, wrap="word", padx=8, pady=6, state=DISABLED)
        self.console_text.grid(row=0, column=0, sticky="nsew")
        ls2 = ttk.Scrollbar(self._console_panel, orient="vertical", command=self.console_text.yview)
        ls2.grid(row=0, column=1, sticky="ns")
        self.console_text.configure(yscrollcommand=ls2.set)
        self.console_text.tag_configure("warn", foreground=C["yellow"])
        self.console_text.tag_configure("err", foreground=C["red"])

        # === Buttons ===
        bf = Frame(mf, bg=C["bg"]); bf.grid(row=6, column=0, sticky="ew", pady=(4,8))
        bf.grid_columnconfigure(0, weight=1)
        sbtn(bf, T("open_folder"), self._on_open_folder, C["bg3"], fs=10, bd=False, padx=14, pady=8).grid(row=0, column=1, padx=(0,8))
        self.download_btn = sbtn(bf, T("download"), self._on_download, C["green"], fs=13, padx=28, pady=10)
        self.download_btn.grid(row=0, column=2)

        mf.grid_rowconfigure(5, weight=1)
        self.status_var.set(T("ready"))

    def _switch_theme(self, name):
        apply_theme(name)
        self.app._rebuild_ui()
        self.w.destroy()

    def _switch_language(self, lang):
        self.i18n.switch(lang)
        self._rebuild_ui()

    def _ol(self, p, t, r, c):
        Label(p, text=t, fg=C["fg2"], bg=C["bg2"], font=("Microsoft YaHei",9), anchor="w").grid(row=r, column=c, sticky="w", padx=(0,2), pady=5)

    def _om(self, p, v, vals, r, c):
        f = Frame(p, bg=C["bg3"]); f.grid(row=r, column=c, sticky="w", pady=5)
        om = OptionMenu(f, v, *vals)
        om.configure(bg=C["bg3"], fg=C["fg"], font=("Consolas",9), relief=FLAT, bd=0, highlightthickness=0, indicatoron=0, padx=6, pady=1)
        om["menu"].configure(bg=C["bg3"], fg=C["fg"], font=("Consolas",9), relief=FLAT)
        om.pack()

    def _oc(self, p, t, v, r, c, s=1, help=None):
        row_frame = Frame(p, bg=C["bg2"])
        row_frame.grid(row=r, column=c, sticky="w", pady=5, columnspan=s)
        cb = Checkbutton(row_frame, text=t, variable=v, bg=C["bg2"], fg=C["fg"], selectcolor=C["bg3"],
            activebackground=C["bg2"], activeforeground=C["fg"], font=("Microsoft YaHei",9),
            relief=FLAT, bd=0, cursor="hand2")
        cb.pack(side=LEFT)
        if help:
            hicon = Label(row_frame, text="?", bg=C["bg2"], fg=C["fg2"],
                font=("Microsoft YaHei", 7, "bold"), cursor="question_arrow")
            hicon.pack(side=LEFT, padx=(0, 4))
            ToolTip(hicon, help)

    def _bind_events(self):
        self.url_entry.bind("<Return>", lambda e: self._on_parse())

    def _open_settings(self):
        SettingsDialog(self.root, self)

    def _log(self, msg, tag="info"):
        now = time.strftime("%H:%M:%S")
        self.log_text.configure(state=NORMAL)
        self.log_text.insert(END, f"[{now}] ", "time")
        self.log_text.insert(END, f"{msg}\n", tag)
        self.log_text.see(END)
        self.log_text.configure(state=DISABLED)

    def _toggle_console(self):
        """切换日志/控制台面板"""
        self._console_visible = not self._console_visible
        if self._console_visible:
            self._log_panel.grid_forget()
            self._console_panel.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,4))
            self._console_btn.configure(text="Log", fg=C["green"])
        else:
            self._console_panel.grid_forget()
            self._log_panel.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0,4))
            self._console_btn.configure(text="Console", fg=C["cyan"])

    def _console_write(self, msg, level="info"):
        """写入控制台面板"""
        tag = level if level in ("warn","err") else "info"
        now = time.strftime("%H:%M:%S")
        self.console_text.configure(state=NORMAL)
        self.console_text.insert(END, f"[{now}] {msg}\n", tag)
        if self._console_visible:
            self.console_text.see(END)
        self.console_text.configure(state=DISABLED)

    def _clear_log(self):
        self.log_text.configure(state=NORMAL)
        self.log_text.delete("1.0", END)
        self.log_text.configure(state=DISABLED)

    def _on_browse_dir(self):
        p = filedialog.askdirectory(title=self._t("output_dir"), initialdir=self.output_dir_var.get())
        if p: self.output_dir_var.set(p); self.downloader.output_dir = p

    def _on_open_folder(self):
        p = self.output_dir_var.get()
        os.startfile(p) if os.path.exists(p) else os.startfile(str(Path.home()/"Downloads"))

    def _on_parse(self):
        T = self._t
        url = self.url_var.get().strip()
        if not url: return
        if "youtube.com" not in url and "youtu.be" not in url:
            self._log(T("invalid_url"), "warn"); return
        self._log(T("parsing_url").format(url[:50]), "info")
        self.status_var.set(T("parsing"))
        self.downloader.set_proxy(self.proxy_var.get())
        # Also pass cookies for parse
        cookie_val = self.cookies_var.get().strip()
        self.downloader.cookies_from_browser = ""
        self.downloader.cookies_file = ""
        if cookie_val:
            if cookie_val in ("chrome", "firefox", "edge", "brave", "opera"):
                self.downloader.cookies_from_browser = cookie_val
            else:
                self.downloader.cookies_file = cookie_val
        def _do():
            info = self.downloader.get_video_info(url)
            if info is None:
                self.root.after(0, lambda: self._log("Parse failed", "err")); return
            if "error" in info:
                err_msg = info["error"]
                hint = ""
                if "SSL" in err_msg or "EOF" in err_msg:
                    hint = chr(10) + T("proxy_hint")
                elif "10048" in err_msg or "address already in use" in err_msg.lower():
                    hint = chr(10) + T("conn_busy")
                self.root.after(0, lambda: [
                    self._log(T("parse_error").format(err_msg + hint), "err"),
                    self.status_var.set(T("parse_fail"))
                ]); return
            self.root.after(0, lambda: self._show_info(info))
        threading.Thread(target=_do, daemon=True).start()

    def _show_info(self, info):
        T = self._t
        dur = info.get("duration", 0)
        txt = f"{T('info_title')}: {info['title']}\n{T('info_author')}: {info['uploader']}  |  {T('info_duration')}: {dur//60}:{dur%60:02d}  |  {T('info_views')}: {info.get('view_count', 0):,}"
        if info.get("formats"):
            # 使用 downloader 中已排序好的 formats，直接取 resolution
            hts = [f["resolution"] for f in info["formats"]]
            txt += f"\n{T('all_resolutions').format(', '.join(hts[:8]))}"

        if not self.info_frame.winfo_ismapped():
            self.info_frame.grid(row=2, column=0, sticky="ew", pady=(0,6))
            ic = card(self.info_frame); ic.pack(fill="x")
            slbl(ic, T("video_info")).grid(row=0, column=0, sticky="w", padx=12, pady=(8,2))
            self.info_text = Text(ic, height=3, bg=C["bg"], fg=C["fg"],
                font=("Microsoft YaHei",9), relief=FLAT, bd=0, state=DISABLED, wrap="word", padx=10, pady=6)
            self.info_text.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,8))
            self._info_card = ic

        self.info_text.configure(state=NORMAL)
        self.info_text.delete("1.0", END); self.info_text.insert("1.0", txt)
        self.info_text.configure(state=DISABLED)
        self.status_var.set(T("parse_ok").format(info['title'][:40]))
        self._log(T("parse_ok").format(info['title'][:50]), "ok")

    def _animate_progress(self, pct):
        w = max(self.pc.winfo_width(), 10)
        fw = int(w * pct / 100)
        self.pc.coords(self._pb, 0, 0, fw, 14)
        if pct < 40: color = self._ic(C["green"], C["yellow"], pct/40)
        elif pct < 80: color = self._ic(C["yellow"], C["accent"], (pct-40)/40)
        else: color = self._ic(C["accent"], C["green"], (pct-80)/20)
        self.pc.itemconfig(self._pb, fill=color)
        self.pc.coords(self._pt, w//2, 7)
        self.pc.itemconfig(self._pt, text=f"{pct:.0f}%")

    def _ic(self, c1, c2, t):
        t = max(0, min(1, t))
        r1,g1,b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
        r2,g2,b2 = int(c2[1:3],16), int(c2[3:5],16), int(c2[5:7],16)
        return f"#{int(r1+(r2-r1)*t):02x}{int(g1+(g2-g1)*t):02x}{int(b1+(b2-b1)*t):02x}"

    def _fs(self, s):
        if not s: return ""
        if s>=1048576: return f"{s/1048576:.1f} MiB/s"
        if s>=1024: return f"{s/1024:.1f} KiB/s"
        return f"{s:.0f} B/s"

    def _fz(self, s):
        if s==0: return "?"
        if s>=1073741824: return f"{s/1073741824:.1f} GiB"
        if s>=1048576: return f"{s/1048576:.1f} MiB"
        if s>=1024: return f"{s/1024:.1f} KiB"
        return f"{s} B"

    def _fe(self, e):
        if not e or e<=0: return ""
        m,s=divmod(e,60); h,m=divmod(m,60)
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"

    def _on_progress(self, data):
        T = self._t
        if data["type"] == "extracting":
            self.root.after(0, lambda: self.status_var.set(T("extracting")))
        elif data["type"] == "download":
            pct = data["percent"]
            self.root.after(0, lambda: self.progress_var.set(pct))
            self.root.after(0, lambda: self._animate_progress(pct))
            self.root.after(0, lambda: self.speed_label.configure(
                text=f"{T('speed')}: {self._fs(data['speed'])}  |  {T('eta')}: {self._fe(data['eta'])}  |  {T('downloaded')}: {self._fz(data['downloaded'])} / {self._fz(data['total'])}"))
        elif data["type"] == "processing":
            self.root.after(0, lambda: self.status_var.set(T("merging")))
            self.root.after(0, lambda: self._log(T("merging"), "progress"))

    def _on_download(self):
        T = self._t
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", T("invalid_url"))
            return
        self.downloading = True
        self.download_btn.configure(text=T("downloading"), state=DISABLED, bg=C["bg3"])
        self.progress_var.set(0); self._animate_progress(0)
        self.speed_label.configure(text=""); self.status_var.set(T("connecting"))
        self._log(T("download_start").format(url[:50]), "ok")
        self.downloader.output_dir = self.output_dir_var.get()
        self.downloader.set_proxy(self.proxy_var.get())
        self.downloader.set_gpu(self.gpu_enabled_var.get())
        self.downloader.on_progress(self._on_progress)
        self.downloader.set_console(self.console_enabled_var.get(), self._console_write)
        # Setup cookies
        cookie_val = self.cookies_var.get().strip()
        self.downloader.cookies_from_browser = ""
        self.downloader.cookies_file = ""
        if cookie_val:
            if cookie_val in ("chrome", "firefox", "edge", "brave", "opera"):
                self.downloader.cookies_from_browser = cookie_val
            else:
                self.downloader.cookies_file = cookie_val
        # Pass settings to downloader
        self.downloader.set_options(
            multi_thread=self.multi_thread_var.get(),
            threads=self.threads_var.get(),
            use_aria2=self.use_aria2_var.get(),
            force_ipv4=self.force_ipv4_var.get(),
        )

        def _do():
            try:
                self.root.after(0, lambda: self.status_var.set(T("extracting")))
                self.root.after(0, lambda: self._log(T("extracting"), "info"))
                result = self.downloader.download(
                    url=url, quality=self.quality_var.get(), format_type=self.format_var.get(),
                    audio_only=self.audio_only_var.get(), subtitles=self.subtitle_var.get(),
                    subtitle_langs=self.sub_lang_var.get(), playlist=self.playlist_var.get())
                self.current_file = result if result and os.path.isfile(result) else None
                tp = None; ml = None
                if self.make_torrent_var.get() and self.current_file:
                    self.root.after(0, lambda: self.status_var.set(T("creating_torrent")))
                    self.root.after(0, lambda: self._log(T("creating_torrent"), "progress"))
                    tp = self.torrent_maker.create(self.current_file)
                    ml = self.torrent_maker.create_magnet(tp)
                def _done():
                    self.progress_var.set(100); self._animate_progress(100)
                    self.status_var.set(T("download_complete"))
                    self.downloading = False
                    self.download_btn.configure(text=T("download"), state=NORMAL, bg=C["green"])
                    if self.current_file:
                        fn = os.path.basename(self.current_file)
                        self._log(T("download_done").format(fn, self._fz(os.path.getsize(self.current_file))), "ok")
                        if messagebox.askyesno(T("download_complete"), f"{fn}\n\n{T('open_folder_q')}"):
                            os.startfile(os.path.dirname(self.current_file))
                    elif result:
                        self._log(f"{T('download_done')}: {result}", "ok")
                    if tp: self._log(T("torrent_done").format(tp), "ok")
                    if ml: self._log(T("magnet_done").format(ml[:80]), "ok")
                self.root.after(0, _done)
            except Exception as e:
                def _err():
                    self.downloading = False
                    self.download_btn.configure(text=T("retry"), state=NORMAL, bg=C["accent"])
                    self.status_var.set(f"Error: {str(e)[:50]}")
                    self._log(T("download_fail").format(str(e)), "err")
                    messagebox.showerror("Error", str(e))
                self.root.after(0, _err)
        threading.Thread(target=_do, daemon=True).start()


def main():
    root = Tk()
    setup_styles()
    YouTubeDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
