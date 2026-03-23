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
import PIL.ImageFilter
from PIL import ImageGrab
import customtkinter as ctk
from datetime import datetime


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


#Temp Data
SONGS=[
    (1,  "Instant Crush",           "Daft Punk",        "Random Access Memories",          337),
    (2,  "Get Lucky",               "Daft Punk",        "Random Access Memories",          369),
    (4,  "Harder Better Faster",    "Daft Punk",        "Discovery",                       224),
    (7,  "The Pretender",           "Foo Fighters",     "Echoes Silence Patience & Grace", 269),
    (8,  "Learn to Fly",            "Foo Fighters",     "There Is Nothing Left To Lose",   235),
    (9,  "Everlong",                "Foo Fighters",     "The Colour And The Shape",        250),
    (11, "Karma Police",            "Radiohead",        "OK Computer",                     261),
    (14, "Creep",                   "Radiohead",        "Pablo Honey",                     238),
    (20, "Do I Wanna Know?",        "Arctic Monkeys",   "AM",                              272),
    (21, "R U Mine?",               "Arctic Monkeys",   "AM",                              200),
    (30, "Something Human",         "Muse",             "Simulation Theory",               214),
    (40, "Sweater Weather",         "The Neighbourhood","I Love You",                      242),
    (45, "Enter Sandman",           "Metallica",        "Metallica",                       331),
    (50, "Smells Like Teen Spirit", "Nirvana",          "Nevermind",                       301),
]

PLAYLISTS=[
    (1, "Favourites", "/home/ng8/.cache/oap/covers/51.jpg"),
    (2, "Chill",      "/home/ng8/.cache/oap/covers/81.jpg"),
    (3, "Workout",    "/home/ng8/.cache/oap/covers/87.jpg"),
    (4, "Road Trip",  "/home/ng8/.cache/oap/covers/70.jpg"),
]

HISTORY=[
    (181, "2026-03-20 11:06:04", 820),
    (23,  "2026-03-20 11:06:04", 0),
    (114, "2026-03-20 11:06:04", 0),
    (73,  "2026-03-20 11:06:04", 0),
    (63,  "2026-03-20 11:06:04", 0),
]


#code
class initial(ctk.CTk):
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

        self.main=MainUI(self)
        self.main.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.ForceClose)

    def ForceClose(self):
        self.destroy()
        sys.exit(0)

class MainUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.SideBar=ctk.CTkFrame(self, width=int(240*MOD), corner_radius=0, fg_color=SideBarColor)
        self.SideBar.grid(row=0, column=0, sticky="nsew")
        self.SideBar.pack_propagate(False)

        ctk.CTkFrame(self.SideBar, height=int(30*MOD), fg_color="transparent").pack()

        self.NavButtons = {}
        self.AddNav("All Music", AllMusic)
        self.AddNav("Playlist", Playlist)
        self.AddNav("History", History)
        
        ctk.CTkFrame(self.SideBar, fg_color="transparent").pack(fill="y", expand=True)
        self.AddNav("Settings", Settings)

        ctk.CTkFrame(self.SideBar, height=int(30*MOD), fg_color="transparent").pack()
        
        self.MainArea=ctk.CTkFrame(self, fg_color="transparent")
        self.MainArea.grid(row=0, column=1, sticky="nsew", padx=int(30*MOD), pady=int(30*MOD))
        self.MainArea.pack_propagate(False)
        
        self.frames={}
        self.current_frame=None
        
        self.ShowFrame("All Music")
        
    def AddNav(self, name, frame_class):
        btn=SideBar(self.SideBar, name, command=lambda n=name:self.ShowFrame(n))
        btn.pack(side="top", pady=int(2*MOD), padx=int(10*MOD))
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
        self.But_BG.pack(fill="both", padx=int(10*MOD))

        self.indicator=ctk.CTkFrame(self.But_BG, width=int(7*MOD), height=int(40*MOD), corner_radius=6, fg_color=SelectColor if is_active else AccentColor)
        self.indicator.pack(side="left", padx=(int(10*MOD), int(10*MOD)))

        self.label=ctk.CTkLabel(self.But_BG, text=text, anchor="w", text_color=TextColor if is_active else SubTextColor, font=("Ubuntu", int(35*MOD), "bold" if is_active else "normal"))
        self.label.pack(side="left", fill="both", pady=(int(10*MOD),int(10*MOD)))

        self.bind("<Button-1>", self.OnClick)
        self.label.bind("<Button-1>", self.OnClick)
        self.indicator.bind("<Button-1>", self.OnClick)

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.But_BG.configure(fg_color=SelectColor if active else "transparent", border_width=1 if active else 0)
        self.indicator.configure(fg_color=ActiveColor if active else AccentColor)
        self.label.configure(text_color=TextColor if active else SubTextColor, font=("Ubuntu", int(35*MOD), "bold" if active else "normal"))

class AllMusic(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command
        self.data=TempData()

        header=ctk.CTkFrame(self, fg_color="transparent", height=int(50*MOD))
        header.pack(fill="x", pady=(0, int(20*MOD)))
        header.pack_propagate(False)

        self.AddSbtn=ctk.CTkButton(header, text="+", height=int(40*MOD), width=int(40*MOD), fg_color=SelectColor if is_active else SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, text_color=SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.AddMusic)
        self.AddSbtn.pack(side="right", padx=(5*MOD, 0))

        self.FltBtn=ctk.CTkButton(header, text="F", height=int(40*MOD), width=int(40*MOD), fg_color=SelectColor if is_active else SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, text_color=SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.Filter)
        self.FltBtn.pack(side="left", padx=(0, int(5*MOD)))

        self.Search=ctk.CTkEntry(header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=int(40*MOD), fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal"))
        self.Search.pack(side="left", fill="x", expand=True)
        self.Search.bind("<KeyRelease>", self.OnSearch)

        self.scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.DispSong()

    def DispSong(self):##
        data=self.data.get_songs()
        
        for i in range(len(data)):
            s=data[i % len(data)]
            DispSong(self.scroll, s[0], s[1], s[2])

    def OnSearch(self):
        pass

    def AddMusic(self):
        self.overlay=AM_AddMusic(self.winfo_toplevel())

    def Filter(self):
        pass

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.AddSbtn.configure(fg_color=SelectColor if active else SideBarColor)
        self.FltBtn.configure(fg_color=SelectColor if active else SideBarColor)

class AM_AddMusic(ctk.CTkFrame):
    def __init__(self, master, back=None):
        root=master.winfo_toplevel()
        root.update_idletasks()
    
        x,y,w,h=root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        img=ImageGrab.grab(bbox=(x,y,x+w,y+h))
        img=img.filter(PIL.ImageFilter.GaussianBlur(10))
    
        self.bg_img=ctk.CTkImage(img, size=(w,h))
        self.backdrop=ctk.CTkLabel(master, image=self.bg_img, text="")
        self.backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        self.backdrop.bind("<Button-1>", lambda e: self.Close())
    
        super().__init__(root, fg_color=SideBarColor, corner_radius=12, border_color=AccentColor, border_width=1)
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)

    def Close(self):
        self.backdrop.destroy()
        self.destroy()

class Playlist(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command
        self.data=TempData()

        self.header=ctk.CTkFrame(self, fg_color="transparent", height=int(50*MOD))
        self.header.pack(fill="x", pady=(0, int(20*MOD)))
        self.header.pack_propagate(False)

        self.AddPlaylBtn=ctk.CTkButton(self.header, text="+", height=int(40*MOD), width=int(40*MOD), fg_color=SelectColor if is_active else SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, text_color=SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.AddPlaylist)
        self.AddPlaylBtn.pack(side="right", padx=(int(5*MOD), 0))

        ctk.CTkEntry(self.header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=int(40*MOD), fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal")).pack(side="left", fill="x", expand=True)

        self.scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.PlaylistDisp()

    def PlaylistDisp(self):
        data=self.data.get_playlists()

        for s in data:
            P_PlaylistDisp(self.scroll, s[0], s[1], s[2], on_open=self.OpenPlaylist)

    def AddPlaylist(self):
        self.overlay=AM_AddMusic(self.winfo_toplevel())

    def CloseAddPlaylist(self):
        self.overlay.destroy()

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.AddPlaylBtn.configure(fg_color=SelectColor if active else SideBarColor)

    def OpenPlaylist(self, PlaylistSno, PlaylistName, CoverDir):
        self.header.pack_forget()
        self.scroll.pack_forget()
        self.current_playlist=P_FullPlaylistView(self, PlaylistSno, PlaylistName, CoverDir, back=self.ClosePlaylist)
        self.current_playlist.pack(fill="both", expand=True)

    def ClosePlaylist(self):
        self.current_playlist.pack_forget()
        self.current_playlist=None
        self.header.pack(fill="x", pady=(0, int(20*MOD)))
        self.scroll.pack(fill="both", expand=True)

class P_PlaylistDisp(ctk.CTkFrame):
    def __init__(self, master, PlaylistSno, PlaylistName, CoverDir, on_open=None):
        super().__init__(master)
        self.configure(fg_color=SideBarColor, height=120*MOD, corner_radius=8)
        self.pack(fill="x", pady=2*MOD)
        self.pack_propagate(False)

        self.PlaylistSno=PlaylistSno
        self.PlaylistName=PlaylistName
        self.CoverDir=CoverDir
        self.on_open=on_open

        #art=Image.open()
        art=None
        if art is None:
            art = Image.new("RGB", (45,45), color=(40, 40, 40))
        self.cover_img=ctk.CTkImage(art, size=(int(100*MOD), int(100*MOD)))
        self.cover_art=ctk.CTkLabel(self, image=self.cover_img, text="")
        self.cover_art.pack(side="left", padx=(10*MOD, 10*MOD))

        self.info=ctk.CTkFrame(self, fg_color="transparent")
        self.info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(self.info, text=self.PlaylistName, anchor="w", text_color=TextColor, font=("Ubuntu", int(15*MOD), "bold")).pack(fill="x", pady=(int(8*MOD), 0), padx=(5*MOD,0))

        self.options_but=ctk.CTkButton(self, text=">", width=int(30*MOD), height=int(30*MOD), hover_color=HoverColor, fg_color="transparent", text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.GoToPlaylist)
        self.options_but.pack(side="right", padx=(10*MOD, 10*MOD))

    def GoToPlaylist(self):
        if self.on_open: self.on_open(self.PlaylistSno, self.PlaylistName, self.CoverDir)

class P_FullPlaylistView(ctk.CTkFrame):
    def __init__(self, master, PlaylistSno, PlaylistName, CoverDir, back=None):
        super().__init__(master, fg_color="transparent")
        self.pack(fill="both", expand=True)
        self.PlaylistSno=PlaylistSno
        self.PlaylistName=PlaylistName
        self.CoverDir=CoverDir

        art=Image.new("RGB", (200,200), color=(40,40,40))

        self.PlaylistInfo=ctk.CTkFrame(self, fg_color=SideBarColor)
        self.PlaylistInfo.pack(fill="x")

        ctk.CTkButton(self.PlaylistInfo, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=10)

        self.cover_img=ctk.CTkImage(art, size=(int(200*MOD), int(200*MOD)))
        self.cover_art=ctk.CTkLabel(self.PlaylistInfo, image=self.cover_img, text="")
        self.cover_art.pack(side="left", padx=(int(10*MOD), int(10*MOD)))

        ctk.CTkLabel(self.PlaylistInfo, text=PlaylistName, anchor="w", text_color=TextColor, font=("Ubuntu", int(25*MOD), "bold")).pack(side="left", pady=(int(4*MOD), 0), padx=(int(5*MOD),0))

        self.options=ctk.CTkFrame(self.PlaylistInfo, fg_color="transparent")
        self.options.pack(side="right", padx=(10,10))
        ctk.CTkButton(self.options, width=int(100*MOD), height=int(35*MOD), corner_radius=6, fg_color=AccentColor, hover_color=HoverColor, text_color=TextColor, font=("Ubuntu", int(15*MOD)), text="CN").pack(side="left", padx=3)
        ctk.CTkButton(self.options, width=int(100*MOD), height=int(35*MOD), corner_radius=6, fg_color=AccentColor, hover_color=HoverColor, text_color=TextColor, font=("Ubuntu", int(15*MOD)), text="CA").pack(side="left", padx=3)
        ctk.CTkButton(self.options, width=int(100*MOD), height=int(35*MOD), corner_radius=6, fg_color=AccentColor, hover_color=HoverColor, text_color=TextColor, font=("Ubuntu", int(15*MOD)), text="DP").pack(side="left", padx=3)

        self.scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True)

        self.GetDispSong()

    def GetDispSong(self):
        data=TempData().get_playlist_songs(self.PlaylistSno)
        for s in data:
            DispSong(self.scroll, s[0], s[1], s[2])

class P_NoMusicDisp(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="transparent")

        ctk.CTkLabel(self.scroll, text="No Playlists...", anchor="w", fg_color="transparent", text_color=SubTextColor, font=("Ubuntu", int(20*MOD), "normal"))

class P_MakePlaylist(ctk.CTkFrame):
    def __init__(self, master, back=None):
        root=master.winfo_toplevel()
        root.update_idletasks()
    
        x,y,w,h=root.winfo_rootx(), root.winfo_rooty(), root.winfo_width(), root.winfo_height()
        img=ImageGrab.grab(bbox=(x,y,x+w,y+h))
        img=img.filter(PIL.ImageFilter.GaussianBlur(10))
    
        self.bg_img=ctk.CTkImage(img, size=(w,h))
        self.backdrop=ctk.CTkLabel(master, image=self.bg_img, text="")
        self.backdrop.place(x=0, y=0, relwidth=1, relheight=1)
        self.backdrop.bind("<Button-1>", lambda e: self.Close())
    
        super().__init__(root, fg_color=SideBarColor, corner_radius=12, border_color=AccentColor, border_width=1)
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.6)

    def Close(self):
        self.backdrop.destroy()
        self.destroy()

class History(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command
        
        self.TabBG=ctk.CTkFrame(self, fg_color=SideBarColor, corner_radius=8, border_color=AccentColor, border_width=1)
        self.TabBG.pack(fill="x", pady=(0, int(20*MOD)))
        self.TabBG.grid_columnconfigure((0, 1), weight=1)
        self.TabBG.grid_rowconfigure(0, weight=1)

        self.HisBut=ctk.CTkButton(self.TabBG, text="History", fg_color=SelectColor if is_active else "transparent", hover_color=HoverColor, border_color=AccentColor, border_width=1 if is_active else 0, corner_radius=6, text_color=TextColor if is_active else SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.ShowHistory)
        self.HisBut.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        self.StatBut=ctk.CTkButton(self.TabBG, text="Stats", fg_color=SelectColor if is_active else "transparent", hover_color=HoverColor, border_color=AccentColor, border_width=1 if is_active else 0, corner_radius=6, text_color=TextColor if is_active else SubTextColor, font=("Ubuntu", int(30*MOD), "bold"), command=self.ShowStats)
        self.StatBut.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

        scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

    def ShowHistory(self):
        pass

    def ShowStats(self):
        pass

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.HisBut.configure(fg_color=SelectColor if active else "transparent", border_width=1 if active else 0, text_color=TextColor if active else SubTextColor)
        self.StatBut.configure(fg_color=SelectColor if active else "transparent", border_width=1 if active else 0, text_color=TextColor if active else SubTextColor)

class H_RawHistory(ctk.CTkFrame):
    pass

class H_Stats(ctk.CTkFrame):
    pass

class Settings(ctk.CTkFrame):
    def __init__(self, master, command=None, is_active=False):
        super().__init__(master, fg_color="transparent")
        self.command=command

        self.header=ctk.CTkFrame(self, fg_color="transparent", height=int(50*MOD))
        self.header.pack(fill="x", pady=(0, int(20*MOD)))
        self.header.pack_propagate(False)
        ctk.CTkEntry(self.header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=int(40*MOD), fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal")).pack(side="left", fill="x", expand=True)

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
        self.TrmBG.pack(fill="x", pady=(int(10*MOD), 0))
        self.label=ctk.CTkLabel(self.TrmBG, text="Terminal", anchor="w", text_color=TextColor, font=("Ubuntu", int(30*MOD), "bold"))
        self.label.pack(fill="x", padx=int(10*MOD), pady=(int(10*MOD), int(5*MOD)))
        self.Search=ctk.CTkEntry(self.TrmBG, placeholder_text="Cmd...", placeholder_text_color=SubTextColor, text_color=TextColor, height=int(40*MOD), fg_color=SideBarColor, border_color=AccentColor, border_width=2, corner_radius=8, font=("Ubuntu", int(20*MOD), "normal"))
        self.Search.pack(fill="x", padx=int(10*MOD), pady=(0, int(10*MOD)))

        ctk.CTkFrame(self.scroll, height=int(30*MOD), fg_color="transparent").pack()
        
        self.frames={}
        self.current_frame=None
        
    def AddNav(self, name, frame_class):
        btn=S_Menue(self.scroll, name, command=lambda n=name:self.ShowFrame(n))
        btn.pack(fill="x", pady=2)
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
        self.header.pack(fill="x", pady=(0, int(20*MOD)))
        self.scroll.pack(fill="both", expand=True)

class S_Menue(ctk.CTkFrame):
    def __init__(self, master, text, command=None):
        super().__init__(master, fg_color= "transparent")
        self.command=command

        self.Butt=ctk.CTkButton(self, text=text, anchor="w", height=int(55*MOD), text_color= TextColor, fg_color=SideBarColor, hover_color=HoverColor, border_color=AccentColor, border_width=1, corner_radius=8, font=("Ubuntu", int(30*MOD), "bold"), command=command)
        self.Butt.pack(fill="x", pady=(int(10*MOD), 0))

        self.bind("<Button-1>", self.OnClick)
        
    def OnClick(self, event):
        if self.command: self.command()

class S_Personalise(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

        row1=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Theme").pack(side="left", padx=20)
        ctk.CTkOptionMenu(row1, values=["System", "Dark", "Light"], width=100, height=23, command=self.change_theme).pack(side="right", padx=20)

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

class S_Sound(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

class S_Network(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

class S_History(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

class S_Notifications(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

class S_KeyboardShortcut(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

class S_About(ctk.CTkFrame):
    def __init__(self, master, back=None):
        super().__init__(master, fg_color="transparent")

        row=ctk.CTkFrame(self, fg_color=SideBarColor, height=int(80*MOD))
        row.pack(fill="x", pady=5)
        ctk.CTkButton(row, text="← Back", fg_color="transparent", hover_color=SideBarColor, text_color=SubTextColor, font=("Ubuntu", int(15*MOD)), command=back).pack(side="left", padx=20)

class S_Terminal:#?
    pass

class FullScreenPlayer(ctk.CTkFrame):#?
    pass

class PIPplayer():#?
    pass

class DispSong(ctk.CTkFrame):
    def __init__(self, master, SongSno, title, artist):
        super().__init__(master)
        self.configure(fg_color="transparent", height=int(60*MOD))
        self.pack(fill="x", pady=2)
        self.pack_propagate(False)
        self.SongSno=SongSno

        art = Image.new("RGB", (45,45), color=(40, 40, 40))
        self.cover_img=ctk.CTkImage(art, size=(int(45*MOD), int(45*MOD)))
        self.cover_art=ctk.CTkLabel(self, image=self.cover_img, text="")
        self.cover_art.pack(side="left", padx=(int(10*MOD), int(10*MOD)))

        self.info=ctk.CTkFrame(self, fg_color="transparent")
        self.info.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(self.info, text=title, anchor="w", text_color=TextColor, font=("Ubuntu", int(15*MOD), "bold")).pack(fill="x", pady=(4*MOD, 0), padx=(5*MOD,0))
        ctk.CTkLabel(self.info, text=artist, anchor="w", text_color=SubTextColor, font=("Ubuntu", int(12*MOD))).pack(fill="x", padx=(5*MOD,0))

        self.options_but=ctk.CTkButton(self, text=">", width=int(30*MOD), height=int(30*MOD), hover_color=HoverColor, fg_color="transparent", text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.LessOptions)
        self.options_but.pack_forget()
        self.AddToQueue=ctk.CTkButton(self, width=4, height=int(35*MOD), corner_radius=6, fg_color=SubTextColor, font=("Ubuntu", int(20*MOD)), hover_color=SubTextColor, text="", command=self.MoreOptions)
        self.AddToQueue.pack(side="right", padx=(3, int(10*MOD)))
        self.AddToPlaylist=ctk.CTkButton(self, width=4, height=int(35*MOD), corner_radius=6, fg_color=SubTextColor, hover_color=SubTextColor, text="", command=self.MoreOptions) 
        self.AddToPlaylist.pack(side="right", padx=(3, 0))
        self.EditMetadata=ctk.CTkButton(self, width=4, height=int(35*MOD), corner_radius=6, fg_color=SubTextColor, hover_color=SubTextColor, text="", command=self.MoreOptions)
        self.EditMetadata.pack(side="right", padx=(3, 0))
        self.RemoveSong=ctk.CTkButton(self, width=4, height=int(35*MOD), corner_radius=6, fg_color=SubTextColor, hover_color=SubTextColor, text="", command=self.MoreOptions)
        self.RemoveSong.pack(side="right", padx=(int(10*MOD), 0))

    def PlayMusic(self):
        tabel="Songs"
        self.engine.pause()
        self.QDB.ModeNormal(tabel ,(self.SongSno)-1)
        self.engine.load(self.pi.GetDirCsong())
        self.engine.play()
            
    def _fmt(self, seconds):
        if not seconds: return "0:00"
        m, s=divmod(int(seconds), 60)
        return f"{m}:{s:02d}"

    def MoreOptions(self):
        self.configure(height=int(120*MOD), fg_color=SideBarColor, corner_radius=8)
        self.cover_img.configure(size=(100,100))
        self.cover_art.configure(image=self.cover_img)
        self.options_but.pack(side="right")
        self.AddToQueue.configure(text="AQ", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.AddToQueueFN)
        self.AddToPlaylist.configure(text="AP", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.AddToPlaylistFN)
        self.EditMetadata.configure(text="EM", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.EditMetadataFN)
        self.RemoveSong.configure(text="DS", width=int(80*MOD), height=int(100*MOD), fg_color=AccentColor, hover_color=HoverColor, text_color=SubTextColor, font=("Ubuntu", int(20*MOD)), command=self.RemoveSongFN)

    def LessOptions(self):
        self.configure(height=int(60*MOD), fg_color="transparent")
        self.cover_img.configure(size=(int(45*MOD), int(45*MOD)))
        self.cover_art.configure(image=self.cover_img)
        self.options_but.pack_forget()
        self.AddToQueue.configure(text="", width=int(4*MOD), height=int(35*MOD), fg_color=SubTextColor, hover_color=SubTextColor, command=self.MoreOptions)
        self.AddToPlaylist.configure(text="", width=int(4*MOD), height=int(35*MOD), fg_color=SubTextColor, hover_color=SubTextColor, command=self.MoreOptions)
        self.EditMetadata.configure(text="", width=int(4*MOD), height=int(35*MOD), fg_color=SubTextColor, hover_color=SubTextColor, command=self.MoreOptions)
        self.RemoveSong.configure(text="", width=int(4*MOD), height=int(35*MOD), fg_color=SubTextColor, hover_color=SubTextColor, command=self.MoreOptions)

    def AddToQueueFN(self):
        pass

    def AddToPlaylistFN(self):
        pass

    def EditMetadataFN(self):
        pass

    def RemoveSongFN(self):
        pass

    def refresh(self):
        self.destroy()

class NoMusic(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color="transparent")

        ctk.CTkLabel(self.scroll, text="No Music...", anchor="w", fg_color="transparent", text_color=SubTextColor, font=("Ubuntu", int(20*MOD), "normal"))

class App:
    pass

class TempData:
    def get_songs(self):
        return SONGS
    
    def get_playlists(self):
        return PLAYLISTS
    
    def get_history(self):
        return HISTORY
    
    def search(self, q):
        q=q.lower()
        return [s for s in SONGS if q in s[1].lower() or q in s[2].lower() or q in s[3].lower()]
    
    def get_playlist_songs(self, PlaylistSno):
        return SONGS[:5]

if __name__=="__main__":
    app=App()
    ini=initial()
    ini.mainloop()