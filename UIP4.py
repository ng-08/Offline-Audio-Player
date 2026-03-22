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
    pass

class MainUI(ctk.CTkFrame):
    pass

class AllMusic(ctk.CTkFrame):
    pass

class AM_DispSong(ctk.CTkFrame):
    pass

class AM_NoMusic(ctk.CTkFrame):
    pass

class AM_AddMusic(ctk.CTkFrame):
    pass

class Playlist(ctk.CTKFrame):
    pass

class P_PlaylistDisp(ctk.CTKFrame):
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