#modules
import customtkinter as ctk
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

#color
BGcolor=("#E6E6E6","#151515")
SubBGcolor=("#C0C0C0","#222222")

SideBarColor=("#D8D8D8","#202020")
OutlineColor=("#DDDDDD", "#404040")

AccentColor=("#3B8ED0","#3B8ED0")##

HoverColor=("#D1CECE", "#2B2B2B")

SubHoverColor=("#979797","#333333")
TextColor=("#000000","#FFFFFF")
SubTextColor=("#4E4E4E","#888888")#

#code
class Main(ctk.CTk):
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
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.Basic_UI=BasicUI(self)
        self.Basic_UI.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.ForceClose)

    def ForceClose(self):
        self.destroy()
        sys.exit(0)

class BasicUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=BGcolor)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.SideBar=ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SideBarColor)
        self.SideBar.grid(row=0, column=0, sticky="nsew")
        self.SideBar.pack_propagate(False)

        ctk.CTkFrame(self.SideBar, height=30, fg_color="transparent").pack()

        self.NavButtons = {}
        self.AddNav("All Music", AllMusic)
        self.AddNav("Playlist", Playlist)
        self.AddNav("History", History)
        
        ctk.CTkFrame(self.SideBar, fg_color="transparent").pack(fill="both", expand=True)
        self.AddNav("Settings", Settings)

        ctk.CTkFrame(self.SideBar, height=30, fg_color="transparent").pack()
        
        self.MainArea=ctk.CTkFrame(self, fg_color="transparent")
        self.MainArea.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.MainArea.pack_propagate(False)
        
        self.frames={}
        self.current_frame=None
        
        self.ShowFrame("All Music")
        
    def AddNav(self, name, frame_class):
        btn=SideBar(self.SideBar, name, command=lambda n=name:self.ShowFrame(n))
        btn.pack(side="top", pady=2, padx=10)
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
        super().__init__(master, fg_color="transparent", height=45, corner_radius=6)
        self.pack(fill="x", pady=2, padx=10)
        self.command=command

        self.indicator=ctk.CTkFrame(self, width=4, height=20, corner_radius=2, fg_color=AccentColor if is_active else "transparent")
        self.indicator.pack(side="left", padx=(10, 10))

        self.label=ctk.CTkLabel(self, text=text, anchor="w", text_color=TextColor if is_active else SubTextColor, font=("Segoe UI", 24, "bold" if is_active else "normal"))
        self.label.pack(side="left", fill="both", expand=True)

        self.bind("<Button-1>", self.OnClick)
        self.label.bind("<Button-1>", self.OnClick)
        self.indicator.bind("<Button-1>", self.OnClick)

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.indicator.configure(fg_color=AccentColor if active else "transparent")
        self.label.configure(text_color=TextColor if active else SubTextColor, font=("Segoe UI", 26, "bold" if active else "normal"))

class AllMusic(ctk.CTkFrame):
    pass

class Playlist(ctk.CTkFrame):
    pass

class History(ctk.CTkFrame):
    pass

class SubHistory(ctk.CTkFrame):
    pass

class Stats(ctk.CTkFrame):
    pass

class Settings(ctk.CTkFrame):
    pass

class FirstStartUp:
    pass

if __name__=="__main__":
    main=Main()
    main.mainloop()