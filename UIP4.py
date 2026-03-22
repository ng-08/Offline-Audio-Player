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
    pass

class AM_DispSong(ctk.CTkFrame):
    pass

class AM_NoMusic(ctk.CTkFrame):
    pass

class AM_AddMusic(ctk.CTkFrame):
    pass

class Playlist(ctk.CTkFrame):
    pass

class P_PlaylistDisp(ctk.CTkFrame):
    pass

class P_FullPlaylistView(ctk.CTkFrame):
    pass

class P_MusicDisp(ctk.CTkFrame):
    pass

class P_NoMusicDisp(ctk.CTkFrame):
    pass

class P_MakePlaylist(ctk.CTkFrame):
    pass

class History(ctk.CTkFrame):
    pass

class H_RawHistory(ctk.CTkFrame):
    pass

class H_Stats(ctk.CTkFrame):
    pass

class Settings(ctk.CTkFrame):
    pass

class S_Personalise(ctk.CTkFrame):
    pass

class S_Sound(ctk.CTkFrame):
    pass

class S_Network(ctk.CTkFrame):
    pass

class S_History(ctk.CTkFrame):
    pass

class S_Notifications(ctk.CTkFrame):
    pass

class S_KeyboardShortcut(ctk.CTkFrame):
    pass

class S_About(ctk.CTkFrame):
    pass

class S_Terminal:
    pass

class FullScreenPlayer(ctk.CTkFrame):
    pass

class PIPplayer(ctk.CTkFrame):
    pass

if __name__=="__main__":
    ini=initial()
    ini.mainloop()