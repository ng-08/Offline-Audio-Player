#modules
import customtkinter as ctk
import sys

#colors
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
    pass

class BasicUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")


class SideBar(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")


class AllMusic(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")


class AM_AddMusic(ctk.CTkFrame):
    pass

class Playlist(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")


class P_MakePlaylist(ctk.CTkFrame):
    pass

class History(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")


class H_History(ctk.CTkFrame):
    pass

class H_Stats(ctk.CTkFrame):
    pass

class Settings(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")


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

class MiniPlayer(ctk.CTkFrame):
    pass

class FullScreenPlayer(ctk.CTkFrame):
    pass

if __name__=="__main__":
    ini=Initial()
    ini.mainloop()