#modules
import io
import os
import vlc
import sys
import queue
import base64
import sqlite3
import requests
import threading
from PIL import Image
from mutagen import File
from mutagen.asf import ASF
from mutagen.mp4 import MP4
import customtkinter as ctk
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from datetime import datetime
from mutagen.id3 import ID3, APIC
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from mutagen.asf import ASFByteArrayAttribute

#configs
ctk.set_appearance_mode("Dark")

BGcolor=("#EAEAEA","#151515")
SideBarColor=("#DFDFDF","#202020")
AccentColor=("#BFBFBF","#404040")
ThemeColor=("#3E8DE0")
ActiveColor=ThemeColor
NotActiveColor=("#BBBBBB","#444444")
TextColor=("#000000","#FFFFFF")
SubTextColor=("#222222","#888888")
HoverColor=("#BDBDBD","#424242")
SelectColor=("#DADADA","#252525")

MOD=1

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(__file__)

#code
class Initial(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Music Player")
        
        ScreenWidth=self.winfo_screenwidth()
        ScreenHeight=self.winfo_screenheight()

        AppWidth=int(ScreenWidth*0.70)
        AppHeight=int(ScreenHeight*0.70)
        x=(ScreenWidth//2)-(AppWidth//2)
        y=(ScreenHeight//2)-(AppHeight//2)
        
        self.geometry(f"{AppWidth}x{AppHeight}+{x}+{y}")
        self.configure(fg_color=BGcolor)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.Basic_UI=BasicUI(self)
        self.Basic_UI.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.ForceClose)

    def ForceClose(self):
        self.destroy()
        sys.exit(0)
    
class FirstStartUp:
    def __init__(self):
        self.conn=sqlite3.connect("Music.db")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor=self.conn.cursor()
    
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Directories (
                DirSno INTEGER PRIMARY KEY AUTOINCREMENT,
                FilePath TEXT
            )
        """)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Songs (
                SongSno INTEGER PRIMARY KEY AUTOINCREMENT,
                DirSno INTEGER,
                SubPath TEXT,
                SongFileName TEXT,
                FileType TEXT,
                FOREIGN KEY (DirSno) REFERENCES Directories(DirSno)            
            )
        ''')
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SongData (
                SongSno INTEGER,
                Title TEXT,
                Artist TEXT,
                Album TEXT,
                Duration INTEGER,
                CoverSource INTEGER DEFAULT NULL,
                AltCoverSSNO INTEGER DEFAULT NULL,
                AltCoverPath TEXT DEFAULT NULL,
                TrackNumber INTEGER,
                Year INTEGER,
                Genre TEXT,
                DateAdded TEXT,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
            )
        """)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Queue (
                QueueNo INTEGER PRIMARY KEY AUTOINCREMENT,
                SongSno INTEGER,
                Played INTEGER DEFAULT 0,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS History (
                HistoryNo INTEGER PRIMARY KEY AUTOINCREMENT,
                SongSno INTEGER,
                DatePlayed TEXT,
                DurationPlayed INTEGER,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Playlist (
                PlaylistSno INTEGER PRIMARY KEY AUTOINCREMENT,
                PlaylistName TEXT,
                DateCreated TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Display (
                Sno INTEGER PRIMARY KEY,
                SongSno INTEGER,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
            )
        ''')

        self.conn.commit()

class BasicUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.SideBar=ctk.CTkFrame(self, width=240*MOD, corner_radius=0, fg_color=SideBarColor)
        self.SideBar.grid(row=0, column=0, sticky="nsew")
        self.SideBar.pack_propagate(False)

        ctk.CTkFrame(self.SideBar, height=30*MOD, fg_color="transparent").pack()

        self.NavButtons = {}
        self.AddNav("All Music", AllMusic)
        self.AddNav("Playlist", Playlist)
        self.AddNav("History", History)
        
        ctk.CTkFrame(self.SideBar, fg_color="transparent").pack(fill="y", expand=True)
        self.AddNav("Settings", Settings)

        ctk.CTkFrame(self.SideBar, height=30*MOD, fg_color="transparent").pack()
        
        self.MainArea=ctk.CTkFrame(self, fg_color="transparent")
        self.MainArea.grid(row=0, column=1, sticky="nsew", padx=30*MOD, pady=30*MOD)
        self.MainArea.pack_propagate(False)
        
        self.frames={}
        self.current_frame=None
        
        self.ShowFrame("All Music")
        
    def AddNav(self, name, frame_class):
        btn=SideBar(self.SideBar, name, command=lambda n=name:self.ShowFrame(n))
        btn.pack(side="top", pady=2*MOD, padx=10*MOD)
        self.NavButtons[name]={"btn":btn,"class":frame_class}

    def ShowFrame(self, name):
        for n, data in self.NavButtons.items():
            data["btn"].SetActive(n==name)

        if self.current_frame:
            self.current_frame.pack_forget()

        frame_class=self.NavButtons[name]["class"]
        self.current_frame=frame_class(self.MainArea)
        self.current_frame.pack(fill="both", expand=True)

class SideBar(ctk.CTkFrame):
    def __init__(self, master, text, command=None, is_active=False):
        super().__init__(master, fg_color= "transparent")
        self.pack(fill="x")
        self.command=command

        self.But_BG=ctk.CTkFrame(self, corner_radius=8, fg_color=SelectColor if is_active else "transparent", border_color=AccentColor, border_width=2 if is_active else 0)
        self.But_BG.pack(fill="both", padx=10*MOD)

        self.indicator=ctk.CTkFrame(self.But_BG, width=7*MOD, height=40*MOD, corner_radius=6, fg_color=SelectColor if is_active else AccentColor)
        self.indicator.pack(side="left", padx=(10*MOD, 10*MOD))

        self.label=ctk.CTkLabel(self.But_BG, text=text, anchor="w", text_color=TextColor if is_active else SubTextColor, font=("Ubuntu", 35*MOD, "bold" if is_active else "normal"))
        self.label.pack(side="left", fill="both", pady=(10*MOD,10*MOD))

        self.bind("<Button-1>", self.OnClick)
        self.label.bind("<Button-1>", self.OnClick)
        self.indicator.bind("<Button-1>", self.OnClick)

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.But_BG.configure(fg_color=SelectColor if active else "transparent", border_width=1*MOD if active else 0)
        self.indicator.configure(fg_color=ActiveColor if active else AccentColor)
        self.label.configure(text_color=TextColor if active else SubTextColor, font=("Ubuntu", 35*MOD, "bold" if active else "normal"))

class AllMusic(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command = command
        self.conn=sqlite3.connect("Music.db")
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor=self.conn.cursor()
        self.pi=PlayerInfo(self.conn, self.cursor)

        header=ctk.CTkFrame(self, fg_color="transparent", height=50*MOD)
        header.pack(fill="x", pady=(0, 20*MOD))
        header.pack_propagate(False)

        self.AddSbtn=ctk.CTkButton(header, text="+", height=40*MOD, width=40*MOD, fg_color=SelectColor if is_active else SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, text_color=SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.AddMusic)
        self.AddSbtn.pack(side="right", padx=(5*MOD, 0))

        self.FltBtn=ctk.CTkButton(header, text="F", height=40*MOD, width=40*MOD, fg_color=SelectColor if is_active else SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, text_color=SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.Filter)
        self.FltBtn.pack(side="left", padx=(0, 5*MOD))

        self.Search=ctk.CTkEntry(header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=40*MOD, fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal"))
        self.Search.pack(side="left", fill="x", expand=True)

        self.scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.GetDispSong()

    def GetDispSong(self):
        self.cursor.execute("SELECT SongSno FROM Songs")
        songnos=[row[0] for row in self.cursor.fetchall()]
        data=[]
        for SongSno in songnos:
            self.cursor.execute("SELECT Title, Artist FROM SongData WHERE SongSno = ?", (SongSno,))
            row=self.cursor.fetchone()
            if row:
                data.append((SongSno, row[0], row[1]))

        for i in range(len(data)):
            s=data[i % len(data)]
            AM_DispSong(self.scroll, s[0], s[1], s[2], self.pi, self.conn, self.cursor)

    def AddMusic(self):
        pass

    def Filter(self):
        pass

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.AddSbtn.configure(fg_color=SelectColor if active else SideBarColor)
        self.FltBtn.configure(fg_color=SelectColor if active else SideBarColor)

class AM_DispSong(ctk.CTkFrame):
    def __init__(self, master, SongSno, title, artist, pi, conn, cursor):
        super().__init__(master)
        self.configure(fg_color="transparent", height=60*MOD)
        self.pack(fill="x", pady=2*MOD)
        self.pack_propagate(False)
        self.SongSno=SongSno
        self.pi=pi
        self.conn=conn
        self.cursor=cursor

        self.cursor.execute("SELECT DirSno FROM Songs WHERE SongSno = ?", (SongSno,))
        CSDirNo=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT FilePath FROM Directories WHERE DirSno = ?", (CSDirNo,))
        CSDirFP=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SongFileName FROM Songs WHERE SongSno = ?", (SongSno,))
        CSSFN=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SubPath FROM Songs WHERE SongSno = ?", (SongSno,))
        CSSP=self.cursor.fetchone()[0]
        if CSSP:
            DirACP=f"{CSDirFP}/{CSSP}/{CSSFN}"
        else:
            DirACP=f"{CSDirFP}/{CSSFN}"

        art=self.pi.GetCoverArt(SongSno, DirACP)
        if art is None:
            art = Image.new("RGB", (45,45), color=(40, 40, 40))
        self.cover_img=ctk.CTkImage(art, size=(int(45*MOD), int(45*MOD)))
        self.cover_art=ctk.CTkLabel(self, image=self.cover_img, text="")
        self.cover_art.pack(side="left", padx=(10*MOD, 10*MOD))

        self.info=ctk.CTkFrame(self, fg_color="transparent")
        self.info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(self.info, text=title, anchor="w", text_color=TextColor, font=("Ubuntu", int(15*MOD), "bold")).pack(fill="x", pady=(4*MOD, 0), padx=(5*MOD,0))
        ctk.CTkLabel(self.info, text=artist, anchor="w", text_color=SubTextColor, font=("Ubuntu", int(12*MOD))).pack(fill="x", padx=(5*MOD,0))

        self.options_but=ctk.CTkButton(self, text="⋮", width=int(30*MOD), height=int(30*MOD), hover_color=HoverColor, corner_radius=30, fg_color="transparent", text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.MoreOptions)
        self.options_but.pack(side="right")

    def PlayMusic(self, SongSno):
        pass

    def _fmt(self, seconds):
        if not seconds: return "0:00"
        m, s=divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    def MoreOptions(self):
        self.configure(height=120*MOD, fg_color=SideBarColor, corner_radius=8*MOD)
        self.cover_img.configure(size=(100,100))
        self.cover_art.configure(image=self.cover_img)
        self.options_but.configure(command=self.LessOptions)
        self.AddToQueue=ctk.CTkButton(self, text="AQ", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=None)
        self.AddToQueue.pack(side="right", padx=(8*MOD, 5*MOD))
        self.AddToPlaylist=ctk.CTkButton(self, text="AP", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=None)
        self.AddToPlaylist.pack(side="right", padx=(8*MOD, 0))
        self.EditMetadata=ctk.CTkButton(self, text="EM", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=None)
        self.EditMetadata.pack(side="right", padx=(8*MOD, 0))
        self.DeleteSong=ctk.CTkButton(self, text="DS", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=None)
        self.DeleteSong.pack(side="right", padx=(8*MOD, 0))

    def LessOptions(self):
        self.configure(height=60*MOD, fg_color="transparent")
        self.cover_img.configure(size=(45*MOD, 45*MOD))
        self.cover_art.configure(image=self.cover_img)
        self.options_but.configure(command=self.MoreOptions)
        self.AddToQueue.pack_forget()
        self.AddToPlaylist.pack_forget()
        self.EditMetadata.pack_forget()
        self.DeleteSong.pack_forget()

    def refresh(self):
        self.destroy()

class Playlist(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command

        header=ctk.CTkFrame(self, fg_color="transparent", height=50*MOD)
        header.pack(fill="x", pady=(0, 20*MOD))
        header.pack_propagate(False)

        self.AddPlaylBtn=ctk.CTkButton(header, text="+", height=40*MOD, width=40*MOD, fg_color=SelectColor if is_active else SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, text_color=SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.AddPlaylist)
        self.AddPlaylBtn.pack(side="right", padx=(5*MOD, 0))

        ctk.CTkEntry(header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=40*MOD, fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal")).pack(side="left", fill="x", expand=True)

        scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

    def AddPlaylist(self):
        pass

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.AddPlaylBtn.configure(fg_color=SelectColor if active else SideBarColor)

class P_MakePlaylist(ctk.CTkFrame):
    pass

class History(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command
        
        self.TabBG=ctk.CTkFrame(self, fg_color=SideBarColor, corner_radius=8, border_color=AccentColor, border_width=1*MOD)
        self.TabBG.pack(fill="x", pady=(0, 20*MOD))
        self.TabBG.grid_columnconfigure((0, 1), weight=1)
        self.TabBG.grid_rowconfigure(0, weight=1)

        self.HisBut=ctk.CTkButton(self.TabBG, text="History", fg_color=SelectColor if is_active else "transparent", hover_color=HoverColor, border_color=AccentColor, border_width=1*MOD if is_active else 0, corner_radius=6, text_color=TextColor if is_active else SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.Shistory)
        self.HisBut.grid(row=0, column=0, sticky="nsew", padx=3*MOD, pady=3*MOD)

        self.StatBut=ctk.CTkButton(self.TabBG, text="Stats", fg_color=SelectColor if is_active else "transparent", hover_color=HoverColor, border_color=AccentColor, border_width=1*MOD if is_active else 0, corner_radius=6, text_color=TextColor if is_active else SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.Sstats)
        self.StatBut.grid(row=0, column=1, sticky="nsew", padx=3*MOD, pady=3*MOD)

        scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

    def Shistory(self):
        pass

    def Sstats(self):
        pass

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.HisBut.configure(fg_color=SelectColor if active else "transparent", border_width=1*MOD if active else 0, text_color=TextColor if active else SubTextColor)
        self.StatBut.configure(fg_color=SelectColor if active else "transparent", border_width=1*MOD if active else 0, text_color=TextColor if active else SubTextColor)

class H_History(ctk.CTkFrame):
    pass

class H_Stats(ctk.CTkFrame):
    pass

class Settings(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command

        self.header=ctk.CTkFrame(self, fg_color="transparent", height=50*MOD)
        self.header.pack(fill="x", pady=(0, 20*MOD))
        self.header.pack_propagate(False)

        ctk.CTkEntry(self.header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=40*MOD, fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal")).pack(side="left", fill="x", expand=True)

        self.scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.NavButtons = {}
        self.AddNav("Personalise", S_Personalise)
        self.AddNav("Sound", S_Sound)
        self.AddNav("Network", S_Network)
        self.AddNav("History", S_History)
        self.AddNav("Notification", S_Notifications)
        self.AddNav("Keyboard Shortcuts", S_KeyboardShortcut)
        self.AddNav("About", S_About)

        self.TrmBG=ctk.CTkFrame(self.scroll, corner_radius=8, fg_color=SideBarColor, border_color=AccentColor, border_width=2)
        self.TrmBG.pack(fill="x", pady=(10*MOD, 0))
        self.label=ctk.CTkLabel(self.TrmBG, text="Terminal", anchor="w", text_color=TextColor, font=("Ubuntu", 30*MOD, "bold"))
        self.label.pack(fill="x", padx=10*MOD, pady=(10*MOD, 5*MOD))
        self.Search=ctk.CTkEntry(self.TrmBG, placeholder_text="Cmd...", placeholder_text_color=SubTextColor, text_color=TextColor, height=40*MOD, fg_color=SideBarColor, border_color=AccentColor, border_width=2*MOD, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal"))
        self.Search.pack(fill="x", padx=10*MOD, pady=(0, 10*MOD))

        ctk.CTkFrame(self.scroll, height=30*MOD, fg_color="transparent").pack()
        
        self.frames={}
        self.current_frame=None
        
    def AddNav(self, name, frame_class):
        btn=SettingsMenu(self.scroll, name, command=lambda n=name:self.ShowFrame(n))
        btn.pack(fill="x", pady=2*MOD)
        self.NavButtons[name]={"btn":btn,"class":frame_class}

    def ShowFrame(self, name):
        self.scroll.pack_forget()
        self.header.pack_forget()
        if self.current_frame:
            self.current_frame.pack_forget()
        frame_class=self.NavButtons[name]["class"]
        self.current_frame=frame_class(self, back=self.GoBack)
        self.current_frame.pack(fill="both", expand=True)

    def GoBack(self):
        self.current_frame.pack_forget()
        self.current_frame=None
        self.header.pack(fill="x", pady=(0, 20*MOD))
        self.scroll.pack(fill="both", expand=True)

class SettingsMenu(ctk.CTkFrame):
    def __init__(self, master, text, command=None):
        super().__init__(master, fg_color= "transparent")
        self.command=command

        self.Butt=ctk.CTkButton(self, text=text, anchor="w", height=55*MOD, text_color= TextColor, fg_color=SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1*MOD, corner_radius=8, font=("Ubuntu", int(30*MOD), "bold"), command=command)
        self.Butt.pack(fill="x", pady=(10*MOD, 0))

        self.bind("<Button-1>", self.OnClick)
        
    def OnClick(self, event):
        if self.command: self.command()

class S_Personalise(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))
        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=50)
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text="Theme").pack(side="left", padx=20)
        ctk.CTkOptionMenu(row, values=["System", "Dark", "Light"], width=100, height=23, command=self.change_theme).pack(side="right", padx=20)

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

class S_Sound(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class S_Network(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class S_History(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class S_Notifications(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class S_KeyboardShortcut(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class S_About(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class S_Terminal:
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class MiniPlayer(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")
        ctk.CTkButton(self, text="← Back", fg_color="transparent", hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(anchor="w", pady=(0, 10*MOD))

class FullScreenPlayer(ctk.CTkFrame):
    def __init__(self, master, pi, q, h):
        super().__init__(master)
        self.configure(fg_color=BGcolor)
        self.q=q

        self.h=h

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.pi=pi
        self.engine=AudioEngine()
        self.engine.load(self.pi.GetDirCsong())
        
        self.play_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "play.png")), size=(40*MOD, 40*MOD))
        self.pause_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "pause.png")), size=(40*MOD, 40*MOD))
        self.next_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "next.png")), size=(40*MOD,40*MOD))
        self.prev_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "prev.png")), size=(40*MOD,40*MOD))
        self.shuffle_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "shuffle.png")), size=(40*MOD,40*MOD))

        ctk.CTkFrame(self, height=50*MOD, fg_color="transparent").pack()

        art = self.pi.GetCoverArt(self.pi.GetCsong(), self.pi.GetDirCsong())
        if art is None:
            art = Image.new("RGB", (300, 300), color=(40, 40, 40))
        self.cover_img=ctk.CTkImage(art, size=(300*MOD, 300*MOD))
        self.cover_label=ctk.CTkLabel(self, image=self.cover_img, text="")
        self.cover_label.pack(pady=(40*MOD, 10*MOD))

        ctk.CTkFrame(self, height=50*MOD, fg_color="transparent").pack()

        self.title_label=ctk.CTkLabel(self, text=pi.GetTitle(pi.GetCsong()), font=("Ubuntu", 20*MOD, "bold"), text_color=TextColor)
        self.title_label.pack()
        self.artist_label=ctk.CTkLabel(self, text=pi.GetArtist(pi.GetCsong()), font=("Ubuntu", 14*MOD), text_color=SubTextColor)
        self.artist_label.pack(pady=(2*MOD, 20*MOD))

        ctk.CTkFrame(self, height=30*MOD, fg_color="transparent").pack(fill="both", expand=True)

        self.bar=PlayerBar(self, self.engine)
        self.bar.pack(fill="x", padx=40*MOD)

        controls=ctk.CTkFrame(self, fg_color="transparent")
        controls.pack()

        self.btn_shuffle=ctk.CTkButton(controls, image=self.shuffle_img, text="", width=50*MOD, height=50*MOD, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.ToggleShuffle)
        self.btn_shuffle.pack(side="left")

        self.btn_prev=ctk.CTkButton(controls, image=self.prev_img, text="", width=50*MOD, height=50*MOD, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.TogglePrev)
        self.btn_prev.pack(side="left", padx=10*MOD)

        self.btn_play=ctk.CTkButton(controls, image=self.pause_img, text="", width=60*MOD, height=60*MOD, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.TogglePP)
        self.btn_play.pack(side="left", padx=10*MOD)

        self.btn_next=ctk.CTkButton(controls, image=self.next_img, text="", width=50*MOD, height=50*MOD, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.ToggleNext)
        self.btn_next.pack(side="left", padx=10*MOD)

        ctk.CTkFrame(self, height=20*MOD, fg_color="transparent").pack()

        self.engine.set_end_callback(lambda: self.after(100, self.ToggleNext))

        self.shuffle = False

        self._cover_queue = queue.Queue()
        self.pi.cover_callback = self.RefreshCover
        self._check_cover_queue()

    def TogglePP(self):
        if self.engine.is_playing():
            self.engine.pause()
            self.btn_play.configure(image=self.play_img)
        else:
            self.engine.play()
            self.btn_play.configure(image=self.pause_img)

    def ToggleShuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.q.ModeRandom("Songs")
            self.btn_shuffle.configure(fg_color=ActiveColor)
        else:
            self.q.ModeNormal("Songs", self.pi.GetCsong())
            self.btn_shuffle.configure(fg_color="transparent")
    
    def ToggleNext(self):
        self.q.mark_played(self.pi.GetCQueueNo())

        self.h.RecHistory(self.pi.GetCsong())
        
        HNo=self.h.cursor.lastrowid
        self.h.RecDuration(self.engine.player.get_time(), HNo)
        
        Dir=self.pi.GetDirCsong()
        CS=self.pi.GetCsong()

        self.engine.load(Dir)
        self.title_label.configure(text=self.pi.GetTitle(CS))
        self.artist_label.configure(text=self.pi.GetArtist(CS))
        art = self.pi.GetCoverArt(self.pi.GetCsong(), self.pi.GetDirCsong())
        if art is None:
            art = Image.new("RGB", (300, 300), color=(40, 40, 40))
        self.cover_img=ctk.CTkImage(art, size=(300, 300))
        self.cover_label.configure(image=self.cover_img)

        self.q.Refill(1, "Songs")

    def TogglePrev(self):
        pos=self.engine.player.get_time()
        if pos>3000:
            self.engine.player.set_time(0)
        else:
            self.h.RecHistory(self.pi.GetCsong())
        
            HNo=self.h.cursor.lastrowid
            self.h.RecDuration(self.engine.player.get_time(), HNo)

            self.q.un_mark_played(self.pi.GetCQueueNo()-1)

            Dir=self.pi.GetDirCsong()
            CS=self.pi.GetCsong()

            self.engine.load(Dir)
            self.title_label.configure(text=self.pi.GetTitle(CS))
            self.artist_label.configure(text=self.pi.GetArtist(CS))
            art = self.pi.GetCoverArt(self.pi.GetCsong(), self.pi.GetDirCsong())
            if art is None:
                art = Image.new("RGB", (300, 300), color=(40, 40, 40))
            self.cover_img=ctk.CTkImage(art, size=(300, 300))
            self.cover_label.configure(image=self.cover_img)

    def _check_cover_queue(self):
        try:
            while True:
                SongSno = self._cover_queue.get_nowait()
                if self.pi.GetCsong() == SongSno:
                    self._UpdateCover()
        except:
            pass
        self.after(200, self._check_cover_queue)

    def RefreshCover(self, SongSno):
        self._cover_queue.put(SongSno)

    def _UpdateCover(self):
        art = self.pi.GetCoverArt(self.pi.GetCsong(), self.pi.GetDirCsong())
        if art is None:
            art = Image.new("RGB", (300, 300), color=(40, 40, 40))
        self.cover_img = ctk.CTkImage(art, size=(300, 300))
        self.cover_label.configure(image=self.cover_img)

class PlayerInfo:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def GetCsong(self):
        self.cursor.execute("SELECT SongSno FROM Queue WHERE Played = 0 ORDER BY QueueNo Limit 1")
        return self.cursor.fetchone()[0]

    def GetCQueueNo(self):
        self.cursor.execute("SELECT QueueNo FROM Queue WHERE Played=0 ORDER BY QueueNo LIMIT 1")
        return self.cursor.fetchone()[0]

    def GetDirCsong(self):
        CSNo=self.GetCsong()
        self.cursor.execute("SELECT DirSno FROM Songs WHERE SongSno = ?", (CSNo,))
        CSDirNo=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT FilePath FROM Directories WHERE DirSno = ?", (CSDirNo,))
        CSDirFP=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SongFileName FROM Songs WHERE SongSno = ?", (CSNo,))
        CSSFN=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SubPath FROM Songs WHERE SongSno = ?", (CSNo,))
        CSSP=self.cursor.fetchone()[0]
        if CSSP:
            return f"{CSDirFP}/{CSSP}/{CSSFN}"
        else:
            return f"{CSDirFP}/{CSSFN}"

    def GetTitle(self, SongSno):
        self.cursor.execute("SELECT Title FROM SongData WHERE SongSno = ?", (SongSno,))
        Title=self.cursor.fetchone()[0]
        if Title:
            return Title
        else:
            return "N-A"
        
    def GetArtist(self, SongSno):
        self.cursor.execute("SELECT Artist FROM SongData WHERE SongSno = ?", (SongSno,))
        Artist=self.cursor.fetchone()[0]
        if Artist:
            return Artist
        else:
            return "N-A"
        
    def GetCoverArt(self, SongSno, file_path):
        cover = None
        self.cursor.execute("SELECT CoverSource FROM SongData WHERE SongSno = ?", (SongSno,))
        row = self.cursor.fetchone()
        if row[0] == None:
            self.cursor.execute("SELECT Artist, Album FROM SongData WHERE SongSno = ?", (SongSno,))
            CSD=self.cursor.fetchone()
            self.cursor.execute("SELECT SongSno FROM SongData WHERE Artist = ? AND Album = ? AND CoverSource = 1", (CSD[0],CSD[1],))
            X=self.cursor.fetchone()
            X=X[0] if X else None

            if X == None:
                self.cursor.execute("UPDATE SongData SET CoverSource = 3 WHERE SongSno = ?", (SongSno,))
                return self.GetCoverArtWEB(SongSno, CSD[0], CSD[1])

            elif X != None:
                self.cursor.execute("UPDATE SongData SET CoverSource = 2 WHERE SongSno = ?", (SongSno,))
                self.cursor.execute("SELECT DirSno FROM Songs WHERE SongSno = ?", (X,))
                CSDirNo=self.cursor.fetchone()[0]
                self.cursor.execute("SELECT FilePath FROM Directories WHERE DirSno = ?", (CSDirNo,))
                CSDirFP=self.cursor.fetchone()[0]
                self.cursor.execute("SELECT SongFileName FROM Songs WHERE SongSno = ?", (X,))
                CSSFN=self.cursor.fetchone()[0]
                self.cursor.execute("SELECT SubPath FROM Songs WHERE SongSno = ?", (X,))
                CSSP=self.cursor.fetchone()[0]
                if CSSP:
                    DirACP=f"{CSDirFP}/{CSSP}/{CSSFN}"
                else:
                    DirACP=f"{CSDirFP}/{CSSFN}"
                
                return self.GetCoverArtACA(SongSno, X, DirACP)
            
            else:
                self.cursor.execute("UPDATE SongData SET CoverSource = 0 WHERE SongSno = ?", (SongSno,))
                return Image.new("RGB", (300, 300), color=(40, 40, 40))

        elif row[0] == 0:
            return Image.new("RGB", (300, 300), color=(40, 40, 40))

        elif row[0] == 1:
            try:
                if file_path.lower().endswith('.mp3'):
                    tags=MP3(file_path, ID3=ID3)
                    for tag in tags.values():
                        if tag.FrameID=='APIC':
                            cover=Image.open(io.BytesIO(tag.data))

                elif file_path.lower().endswith('.flac'):
                    audio = FLAC(file_path)
                    if audio.pictures:
                        cover = Image.open(io.BytesIO(audio.pictures[0].data))

                elif file_path.lower().endswith('.ogg'):
                    audio = OggVorbis(file_path)
                    if 'metadata_block_picture' in audio:
                        pic = Picture(base64.b64decode(audio['metadata_block_picture'][0]))
                        cover = Image.open(io.BytesIO(pic.data))

                elif file_path.lower().endswith('.wav'):
                    audio = WAVE(file_path)
                    if audio.tags:
                        for tag in audio.tags.values():
                            if tag.FrameID == 'APIC':
                                cover = Image.open(io.BytesIO(tag.data))

                elif file_path.lower().endswith('.m4a'):
                    audio = MP4(file_path)
                    if audio.tags and 'covr' in audio.tags:
                        cover = Image.open(io.BytesIO(bytes(audio.tags['covr'][0])))

                elif file_path.lower().endswith('.opus'):
                    audio = OggOpus(file_path)
                    if 'metadata_block_picture' in audio:
                        pic = Picture(base64.b64decode(audio['metadata_block_picture'][0]))
                        cover = Image.open(io.BytesIO(pic.data))

                elif file_path.lower().endswith('.wma'):
                    audio = ASF(file_path)
                    if 'WM/Picture' in audio.tags:
                        cover = Image.open(io.BytesIO(bytes(audio.tags['WM/Picture'][0].value)))

            except:
                pass

        elif row[0] == 2:
            self.cursor.execute("SELECT AltCoverSSNO FROM SongData WHERE SongSno = ?", (SongSno,))
            X=self.cursor.fetchone()[0]

            self.cursor.execute("SELECT DirSno FROM Songs WHERE SongSno = ?", (X,))
            CSDirNo=self.cursor.fetchone()[0]
            self.cursor.execute("SELECT FilePath FROM Directories WHERE DirSno = ?", (CSDirNo,))
            CSDirFP=self.cursor.fetchone()[0]
            self.cursor.execute("SELECT SongFileName FROM Songs WHERE SongSno = ?", (X,))
            CSSFN=self.cursor.fetchone()[0]
            self.cursor.execute("SELECT SubPath FROM Songs WHERE SongSno = ?", (X,))
            CSSP=self.cursor.fetchone()[0]
            if CSSP:
                DirACP=f"{CSDirFP}/{CSSP}/{CSSFN}"
            else:
                DirACP=f"{CSDirFP}/{CSSFN}"

            cover=self.GetCoverArt(X, DirACP)

            if cover is None:
                self.cursor.execute("UPDATE SongData SET CoverSource = 0 WHERE SongSno = ?", (SongSno,)) 
                self.conn.commit()
                return Image.new("RGB", (300, 300), color=(40, 40, 40))
                
            else:
                pass
            
            return cover
        
        elif row[0] == 3:
            self.cursor.execute("SELECT AltCoverPath, Artist, Album FROM SongData WHERE SongSno = ?", (SongSno,))
            row3 = self.cursor.fetchone()
            path = row3[0]
            if path and os.path.exists(path):
                cover = Image.open(path)
            else:
                return self.GetCoverArtWEB(SongSno, row3[1], row3[2])
        
        self.conn.commit()
        return cover if cover is not None else Image.new("RGB", (300, 300), color=(40, 40, 40))

    def GetCoverArtACA(self, SongSno, X, file_path):
        cover=self.GetCoverArt(X, file_path)

        if cover is None:
            self.cursor.execute("UPDATE SongData SET CoverSource = 0 WHERE SongSno = ?", (SongSno,))
            return Image.new("RGB", (300, 300), color=(40, 40, 40))

        else:
            self.cursor.execute("UPDATE SongData SET AltCoverSSNO = ? WHERE SongSno = ?", (X, SongSno,))
        
        self.conn.commit()
        return cover
    
    def GetCoverArtWEB(self, SongSno, artist, album):
        callback = getattr(self, 'cover_callback', None)
        thread = threading.Thread(target=self._FetchWEB, args=(SongSno, artist, album, callback), daemon=True)
        thread.start()
        return None

    def _FetchWEB(self, SongSno, artist, album, callback=None):
        try:
            conn = sqlite3.connect("Music.db")
            cursor = conn.cursor()

            cache_dir = os.path.expanduser("~/.cache/oap/covers")
            os.makedirs(cache_dir, exist_ok=True)

            cursor.execute("""
                SELECT AltCoverPath FROM SongData
                WHERE Artist = ? AND Album = ? AND AltCoverPath IS NOT NULL
                LIMIT 1
            """, (artist, album))
            existing = cursor.fetchone()
            if existing and os.path.exists(existing[0]):
                cursor.execute("UPDATE SongData SET AltCoverPath = ? WHERE SongSno = ?", (existing[0], SongSno,))
                conn.commit()
                conn.close()
                if callback:
                    callback(SongSno)
                return

            r = requests.get("https://itunes.apple.com/search", params={
                "term": f"{artist} {album}",
                "media": "music",
                "entity": "album",
                "limit": 1
            }, timeout=10)
            results = r.json().get("results", [])
            if not results:
                cursor.execute("UPDATE SongData SET CoverSource = 0 WHERE SongSno = ?", (SongSno,))
                conn.commit()
                conn.close()
                return

            img_url = results[0]["artworkUrl100"].replace("100x100bb", "600x600bb")
            r2 = requests.get(img_url, timeout=10)
            if r2.status_code != 200:
                cursor.execute("UPDATE SongData SET CoverSource = 0 WHERE SongSno = ?", (SongSno,))
                conn.commit()
                conn.close()
                return

            cache_path = os.path.join(cache_dir, f"{SongSno}.jpg")
            with open(cache_path, "wb") as f:
                f.write(r2.content)

            cursor.execute("UPDATE SongData SET AltCoverPath = ? WHERE SongSno = ?", (cache_path, SongSno,))
            conn.commit()
            conn.close()

            if callback:
                callback(SongSno)

        except:
            try:
                cursor.execute("UPDATE SongData SET CoverSource = 0 WHERE SongSno = ?", (SongSno,))
                conn.commit()
                conn.close()
            except:
                pass

class PlayerBar(ctk.CTkFrame):
    def __init__(self, master, engine):
        super().__init__(master, fg_color="transparent")
        self.engine=engine
        self.dragging=False

        self.cur_label=ctk.CTkLabel(self, text="0:00", width=40, text_color=TextColor)
        self.cur_label.pack(side="left")

        self.progress=ctk.CTkProgressBar(self, height=8, progress_color=TextColor, fg_color=SideBarColor)
        self.progress.pack(side="left", fill="x", expand=True, padx=8)
        self.progress.set(0)

        self.dur_label=ctk.CTkLabel(self, text="0:00", width=40, text_color=TextColor)
        self.dur_label.pack(side="left")

        self.progress.bind("<Button-1>", self.on_seek)
        self.progress.bind("<B1-Motion>", self.on_drag)
        self.progress.bind("<ButtonRelease-1>", self.on_release)

        self.update_bar()

    def format_time(self, ms):
        s=ms//1000
        m, s=divmod(s, 60)
        return f"{m}:{s:02d}"

    def on_seek(self, event):
        bar_w=self.progress.winfo_width()
        fraction=max(0, min(1, event.x/bar_w))
        dur=self.engine.player.get_length()
        self.engine.player.set_time(int(fraction*dur))
        self.progress.set(fraction)

    def on_drag(self, event):
        self.dragging=True
        if self.engine.player.is_playing():
            self.engine.player.pause()
        bar_w=self.progress.winfo_width()
        fraction=max(0, min(1, event.x/bar_w))
        dur=self.engine.player.get_length()
        self.progress.set(fraction)
        self.cur_label.configure(text=self.format_time(int(fraction*dur)))

    def on_release(self, event):
        self.dragging=False
        bar_w=self.progress.winfo_width()
        fraction=max(0, min(1, event.x/bar_w))
        dur=self.engine.player.get_length()
        self.engine.player.set_time(int(fraction*dur))
        self.engine.player.play()

    def update_bar(self):
        if not self.dragging:
            pos=self.engine.player.get_time()
            dur=self.engine.player.get_length()
            if dur>0:
                fraction=pos/dur
                self.progress.set(fraction)
                self.cur_label.configure(text=self.format_time(pos))
                self.dur_label.configure(text=self.format_time(dur))
        self.after(100, self.update_bar)

class Database:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def add_directory(self, path):
        self.cursor.execute("INSERT INTO Directories (FilePath) VALUES (?)", (path,))
        self.conn.commit()

    def scan(self):
        self.cursor.execute("SELECT DirSno, FilePath FROM Directories")
        dirs = self.cursor.fetchall()

        for dirSno, dirPath in dirs:
            for root, d, files in os.walk(dirPath):
                for file in files:
                    relative_path=os.path.relpath(root, dirPath)
                    subpath="" if relative_path=="." else relative_path
                    filePath=os.path.join(root, file)
                    
                    try:
                        if filePath.lower().endswith('.mp3'):
                            tags=EasyID3(filePath)
                            duration=int(MP3(filePath).info.length)
                            audio=File(filePath)
                        else:
                            audio=File(filePath)
                            if audio is None:
                                continue
                            tags=audio.tags
                            duration=int(audio.info.length) if audio.info else 0

                        ext=os.path.splitext(file)[1].lower()
                        cover_source = None

                        if ext=='.mp3':
                            cover_source=1 if audio and audio.tags and any(t.FrameID=='APIC' for t in audio.tags.values()) else None
                        elif ext=='.flac':
                            cover_source=1 if audio and audio.pictures else None
                        elif ext in ('.ogg', '.opus'):
                            cover_source=1 if audio and 'metadata_block_picture' in audio else None
                        elif ext=='.wav':
                            cover_source=1 if audio and audio.tags and any(getattr(t,'FrameID','')=='APIC' for t in audio.tags.values()) else None
                        elif ext=='.m4a':
                            cover_source=1 if audio and audio.tags and 'covr' in audio.tags else None
                        elif ext=='.wma':
                            cover_source=1 if audio and audio.tags and 'WM/Picture' in audio.tags else None

                        title=str(tags.get("title", [file])[0]) if tags else file
                        artist=str(tags.get("artist", [""])[0]) if tags else ""
                        album=str(tags.get("album", [""])[0]) if tags else ""
                        genre=str(tags.get("genre", [""])[0]) if tags else ""
                        year=str(tags.get("date", [""])[0]) if tags else ""
                        tracknum=str(tags.get("tracknumber", [""])[0]) if tags else ""

                        self.cursor.execute("""
                            INSERT INTO Songs (DirSno, SubPath, SongFileName, FileType)
                            VALUES (?, ?, ?, ?)
                        """, (dirSno, subpath, file, os.path.splitext(file)[1].lower()))

                        SongSno=self.cursor.lastrowid

                        self.cursor.execute("""
                            INSERT INTO SongData (SongSno, Title, Artist, Album, Duration, CoverSource, TrackNumber, Year, Genre, DateAdded)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (SongSno, title, artist, album, duration, cover_source, tracknum, year, genre, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                    except Exception:
                        continue

        self.conn.commit()

    def close(self):
        self.conn.close()

class QueueDB:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def ModeRandom(self, table):
        self.cursor.execute("DELETE FROM Queue WHERE Played = 0")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY RANDOM() LIMIT 30")
        songs=self.cursor.fetchall()
        for song in songs:
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (song[0],))

        self.conn.commit()

    def ModeNormal(self, table, CurrentSno):
        self.cursor.execute("DELETE FROM Queue WHERE Played = 0")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table} WHERE SongSno > ? ORDER BY SongSno", (CurrentSno,))
        
        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES (?)",(i[0],))
        self.conn.commit()

    def Refill(self, mode, table):
        self.cursor.execute("SELECT COUNT(*) FROM Queue WHERE Played = 0")
        Dif=20-self.cursor.fetchone()[0]
        
        if mode == 1:
            self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY RANDOM() LIMIT ?", (Dif,))
            songs=self.cursor.fetchall()
            for song in songs:
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (song[0],))
                
        elif mode == 2:
            self.cursor.execute(f"SELECT SongSno FROM {table}")

            for i in self.cursor.fetchall():
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES (?)", (i[0],))
            
        self.conn.commit()

    def mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 1 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

    def un_mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 0 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

class DisplayDB:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def Filter(self, table, metric, order):
        self.cursor.execute("DELETE FROM Display")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY {metric} {order}")

        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Display (SongSno) VALUES (?)", (i[0],))
        self.conn.commit()

    def Search(self, table, querry):
        self.cursor.execute("DELETE FROM Display")
        self.conn.commit()

        self.cursor.execute(f'''SELECT SongSno FROM {table} 
                                WHERE Title LIKE ? OR Artist LIKE ? OR Album LIKE ? OR Genre LIKE ?    
                            ''', (f'%{querry}%', f'%{querry}%', f'%{querry}%', f'%{querry}%'))
        
        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Display (SongSno) VALUES (?)", (i[0],))
        self.conn.commit()

    def Populate(self,table):
        self.cursor.execute("DELETE FROM Display")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table}")

        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Display (SongSno) VALUES (?)", (i[0],))
        self.conn.commit()

class PlaylistDB:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def CreatePlaylist(self, placeholder_name):
        self.cursor.execute("SELECT COUNT(*) FROM Playlist WHERE PlaylistName = ?", (placeholder_name,))
        if self.cursor.fetchone()[0] > 0:
            print("Playlist already exists")
            return
        
        else:
            self.cursor.execute(f'''
            CREATE TABLE `{placeholder_name}` (
                Sno INTEGER PRIMARY KEY AUTOINCREMENT,
                SongSno INTEGER,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno) 
            )
            ''')

            self.cursor.execute('''
            INSERT INTO Playlist (PlaylistName, DateCreated)
            VALUES (?, ?)
            ''', (placeholder_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
            self.conn.commit()

    def DeletePlaylist(self, PlaylistSno):
        self.cursor.execute("SELECT COUNT(*) FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        if self.cursor.fetchone()[0] > 0:
            self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
            TabName=self.cursor.fetchone()[0]
            self.cursor.execute(f"DROP TABLE `{TabName}`")
            self.cursor.execute("DELETE FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
            
            self.conn.commit()

        else:
            pass

    def RenamePlaylist(self, PlaylistSno, NewName):
        self.cursor.execute("SELECT COUNT(*) FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        if self.cursor.fetchone()[0] > 0:
            self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
            OldName=self.cursor.fetchone()[0]
            self.cursor.execute("UPDATE Playlist SET PlaylistName = ? WHERE PlaylistSno = ?", (NewName, PlaylistSno,))
            self.cursor.execute(f"ALTER TABLE `{OldName}` RENAME TO `{NewName}`")

            self.conn.commit()

        else:
            pass

    def AddSong(self, PlaylistSno, SongSno):
        self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        x=self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM `{x}` WHERE SongSno = ?", (SongSno,))
        if self.cursor.fetchone()[0]==0:
            self.cursor.execute(f"INSERT INTO `{x}`(SongSno) VALUES(?)", (SongSno,))

            self.conn.commit()

        else:
            pass

    def RemoveSong(self, PlaylistSno, SongSno):
        self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        x=self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM `{x}` WHERE SongSno = ?", (SongSno,))
        if self.cursor.fetchone()[0]>0:
            self.cursor.execute(f"DELETE FROM `{x}` WHERE SongSno = ?", (SongSno,))

            self.conn.commit()

        else:
            pass

    def GetSongs(self, PlaylistSno):
        self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        x=self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT * FROM `{x}`")
        return self.cursor.fetchall()

    def GetAllPlaylists(self):
        self.cursor.execute("SELECT PlaylistName FROM Playlist")
        return self.cursor.fetchall()

class HistoryDB:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def RecHistory(self, SongSno):
        self.cursor.execute('''
        INSERT INTO History (SongSno, DatePlayed)
        VALUES (?, ?)
        ''', (SongSno, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        self.conn.commit()

    def RecDuration(self, duration, HNo):
        self.cursor.execute("UPDATE History SET DurationPlayed = ? WHERE HistoryNo = ?", (duration, HNo,))

        self.conn.commit()

    def GetHistory(self):
        self.cursor.execute("SELECT * FROM History")
        return self.cursor.fetchall()

    def ClearHistory(self):
        self.cursor.execute("DELETE FROM History")
        self.conn.commit()

class MetadataDB:
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor

    def edit(self, SongSno, data):
        data = {k: v for k, v in data.items() if v not in (None, '', [])}

        if not data:
            return False

        self.cursor.execute("""
            SELECT d.FilePath, s.SubPath, s.SongFileName, s.FileType 
            FROM Songs s
            JOIN Directories d ON s.DirSno = d.DirSno
            WHERE s.SongSno = ?
        """, (SongSno,))

        row=self.cursor.fetchone()

        if not row:
            return False
        
        dirPath, subPath, fileName, fileType = row
        filePath = f"{dirPath}/{subPath}/{fileName}" if subPath else f"{dirPath}/{fileName}"

        result = self._write(filePath, fileType, data)
        if result:
            self.UpdateDB(SongSno, data)
        return result

    def _write(self, path, ext, data):
        try:
            if ext == '.mp3':
                try:
                    tags = EasyID3(path)
                except:
                    tags = EasyID3()
                    tags.save(path)
                    tags = EasyID3(path)
                if 'title'       in data: tags['title']       = data['title']
                if 'artist'      in data: tags['artist']      = data['artist']
                if 'album'       in data: tags['album']       = data['album']
                if 'genre'       in data: tags['genre']       = data['genre']
                if 'year'        in data: tags['date']        = data['year']
                if 'tracknumber' in data: tags['tracknumber'] = data['tracknumber']
                tags.save()
                if 'cover_path' in data:
                    full_tags = ID3(path)
                    with open(data['cover_path'], 'rb') as img:
                        img_data = img.read()
                    mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                    full_tags.delall('APIC')
                    full_tags['APIC'] = APIC(encoding=3, mime=mime, type=3, desc='Cover', data=img_data)
                    full_tags.save()

            elif ext == '.flac':
                audio = FLAC(path)
                if 'title'       in data: audio['title']       = data['title']
                if 'artist'      in data: audio['artist']      = data['artist']
                if 'album'       in data: audio['album']       = data['album']
                if 'genre'       in data: audio['genre']       = data['genre']
                if 'year'        in data: audio['date']        = data['year']
                if 'tracknumber' in data: audio['tracknumber'] = data['tracknumber']
                if 'cover_path' in data:
                    pic = Picture()
                    with open(data['cover_path'], 'rb') as img:
                        pic.data = img.read()
                    pic.type = 3
                    pic.mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                    audio.clear_pictures()
                    audio.add_picture(pic)
                audio.save()

            elif ext in ('.ogg', '.opus'):
                audio = OggVorbis(path) if ext == '.ogg' else OggOpus(path)
                if 'title'       in data: audio['title']       = data['title']
                if 'artist'      in data: audio['artist']      = data['artist']
                if 'album'       in data: audio['album']       = data['album']
                if 'genre'       in data: audio['genre']       = data['genre']
                if 'year'        in data: audio['date']        = data['year']
                if 'tracknumber' in data: audio['tracknumber'] = data['tracknumber']
                if 'cover_path' in data and ext == '.ogg':
                    with open(data['cover_path'], 'rb') as img:
                        img_data = img.read()
                    pic = Picture()
                    pic.data = img_data
                    pic.type = 3
                    pic.mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                    audio['metadata_block_picture'] = [base64.b64encode(pic.write()).decode('ascii')]
                audio.save()

            elif ext == '.wav':
                from mutagen.id3 import TIT2, TPE1, TALB, TCON, TDRC, TRCK
                audio = WAVE(path)
                if audio.tags is None:
                    audio.add_tags()
                if 'title'       in data: audio.tags['TIT2'] = TIT2(encoding=3, text=data['title'])
                if 'artist'      in data: audio.tags['TPE1'] = TPE1(encoding=3, text=data['artist'])
                if 'album'       in data: audio.tags['TALB'] = TALB(encoding=3, text=data['album'])
                if 'genre'       in data: audio.tags['TCON'] = TCON(encoding=3, text=data['genre'])
                if 'year'        in data: audio.tags['TDRC'] = TDRC(encoding=3, text=data['year'])
                if 'tracknumber' in data: audio.tags['TRCK'] = TRCK(encoding=3, text=data['tracknumber'])
                if 'cover_path' in data:
                    with open(data['cover_path'], 'rb') as img:
                        img_data = img.read()
                    mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                    audio.tags.delall('APIC')
                    audio.tags['APIC'] = APIC(encoding=3, mime=mime, type=3, desc='Cover', data=img_data)
                audio.save()

            elif ext == '.m4a':
                from mutagen.mp4 import MP4Cover
                audio = MP4(path)
                if audio.tags is None:
                    audio.add_tags()
                if 'title'       in data: audio.tags['\xa9nam'] = [data['title']]
                if 'artist'      in data: audio.tags['\xa9ART'] = [data['artist']]
                if 'album'       in data: audio.tags['\xa9alb'] = [data['album']]
                if 'genre'       in data: audio.tags['\xa9gen'] = [data['genre']]
                if 'year'        in data: audio.tags['\xa9day'] = [data['year']]
                if 'tracknumber' in data: audio.tags['trkn']    = [(int(data['tracknumber']), 0)]
                if 'cover_path' in data:
                    with open(data['cover_path'], 'rb') as img:
                        img_data = img.read()
                    fmt = MP4Cover.FORMAT_JPEG if data['cover_path'].endswith(('.jpg', '.jpeg')) else MP4Cover.FORMAT_PNG
                    audio.tags['covr'] = [MP4Cover(img_data, imageformat=fmt)]
                audio.save()

            elif ext == '.wma':
                audio = ASF(path)
                if 'title'       in data: audio.tags['Title']          = [data['title']]
                if 'artist'      in data: audio.tags['Author']         = [data['artist']]
                if 'album'       in data: audio.tags['WM/AlbumTitle']  = [data['album']]
                if 'genre'       in data: audio.tags['WM/Genre']       = [data['genre']]
                if 'year'        in data: audio.tags['WM/Year']        = [data['year']]
                if 'tracknumber' in data: audio.tags['WM/TrackNumber'] = [data['tracknumber']]
                if 'cover_path' in data:
                    with open(data['cover_path'], 'rb') as img:
                        img_data = img.read()
                    audio.tags['WM/Picture'] = [ASFByteArrayAttribute(img_data)]
                audio.save()

            else:
                return False

            return True
        except Exception:
            return False

    def UpdateDB(self, SongSno, data):
        field_map = {
            'title':       'Title',
            'artist':      'Artist',
            'album':       'Album',
            'genre':       'Genre',
            'year':        'Year',
            'tracknumber': 'TrackNumber',
            'cover_path':  'CoverSource',
        }
        fields = [(field_map[k], 1 if k == 'cover_path' else v) for k, v in data.items() if k in field_map]

        if not fields:
            return
        query = f"UPDATE SongData SET {', '.join(f'{col} = ?' for col, _ in fields)} WHERE SongSno = ?"
        self.cursor.execute(query, [v for _, v in fields] + [SongSno])
        self.conn.commit()

class AudioEngine:
    def __init__(self):
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.current_song = None
        self.events=self.player.event_manager()
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end)
        self._on_end_callback=None

    def load(self, file_path):
        if not os.path.exists(file_path):
            return False
        media = self.vlc_instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()
        self.current_song = file_path
        return True

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def is_playing(self):
        return self.player.is_playing()

    def stop(self):
        self.player.stop()
        self.current_song = None

    def _on_end(self, event):
        if self._on_end_callback:
            self._on_end_callback()

    def set_end_callback(self, callback):
        self._on_end_callback=callback

if __name__=="__main__":
    ini=Initial()
    ini.mainloop()