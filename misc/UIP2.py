#modules
import customtkinter as ctk
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

#color
DARK_COLOR_BG,LIGHT_COLOR_BG = "#121212","#ECECEC"
DARK_COLOR_SIDEBAR,LIGHT_COLOR_SIDEBAR = "#1E1E1E","#E0E0E0"
DARK_COLOR_ACCENT,LIGHT_COLOR_ACCENT = "#3B8ED0","#3B8ED0"
DARK_COLOR_TEXT_MAIN,LIGHT_COLOR_TEXT_MAIN = "#FFFFFF","#A7A7A7"
DARK_COLOR_TEXT_SUB,LIGHT_COLOR_TEXT_SUB = "#888888","#4E4E4E"
DARK_COLOR_HOVER,LIGHT_COLOR_HOVER = "#2B2B2B","#D1CECE"



#Main
class Default(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.BGB=ctk.CTkFrame(self, corner_radius=0, fg_color=('transparent'))
        self.BGB.grid(row=0, column=0, sticky="nsew")
        self.BGB.pack_propagate(False)

        self.MM=ctk.CTkFrame(self, fg_color=('#121212'))
        self.MM.place(relwidth=0.7, relheight=0.7,relx=0.16, rely=0.15)

        self.PT=ctk.CTkLabel(self, text="SETTINGS", font=("Segoe UI", 20, "bold"))
        self.PT.place(relx=0.48, rely=0.2)

        self.btn_close = ctk.CTkButton(self, text="✕", width=25, height=25, fg_color="#AA0000", hover_color="#FF0000")
        self.btn_close.place(relx=0.48, rely=0.2)
    pass

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
        self.configure(fg_color=(LIGHT_COLOR_BG,DARK_COLOR_BG))
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.Basic_UI=BasicUI(self)
        self.Basic_UI.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.ForceClose)

        '''self.Def=Default(self)
        self.Def.grid(row=0, column=0, sticky="nsew")'''

    def ForceClose(self):
        self.destroy()
        sys.exit(0)

class BasicUI(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(fg_color=(LIGHT_COLOR_BG,DARK_COLOR_BG))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.SideBar=ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=(LIGHT_COLOR_SIDEBAR,DARK_COLOR_SIDEBAR))
        self.SideBar.grid(row=0, column=0, sticky="nsew")
        self.SideBar.pack_propagate(False)

        ctk.CTkFrame(self.SideBar, height=30, fg_color="transparent").pack()

        self.NavButtons = {}
        self.AddNav("All Music", MyMusic)
        self.AddNav("Playlist", Playlist)
        self.AddNav("History", History)
        
        ctk.CTkFrame(self.SideBar, fg_color="transparent").pack(fill="both", expand=True)
        self.AddNav("Settings", Settings)
        ctk.CTkFrame(self.SideBar, height=20, fg_color="transparent").pack()
        
        self.MainArea=ctk.CTkFrame(self, fg_color="transparent")
        self.MainArea.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.MainArea.pack_propagate(False)
        
        self.frames={}
        self.current_frame=None
        
        self.ShowFrame("All Music")
        
        self.PIPp=PIPplayer(self)

    def AddNav(self, name, frame_class):
        btn=SideBar(self.SideBar, name, command=lambda n=name:self.ShowFrame(n))
        btn.pack(side="top" if name!="Settings" else "bottom", fill="x", pady=2, padx=10)
        self.NavButtons[name]={"btn":btn,"class":frame_class}

    def ShowFrame(self, name):
        for n, data in self.NavButtons.items():
            data["btn"].SetActive(n==name)

        if self.current_frame:
            self.current_frame.pack_forget()

        frame_class = self.NavButtons[name]["class"]
        self.current_frame = frame_class(self.MainArea)
        self.current_frame.pack(fill="both", expand=True)

    def BuildUI(self):
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")
        
        self.btn1 = ctk.CTkButton(self.sidebar, text="My Music")
        self.btn1.pack(pady=20)

        self.main_view = ctk.CTkFrame(self)
        self.main_view.pack(side="right", fill="both", expand=True)
        
class SideBar(ctk.CTkFrame):
    def __init__(self, master, text, command=None, is_active=False):
        super().__init__(master, fg_color="transparent", height=45, corner_radius=6)
        self.pack(fill="x", pady=2, padx=10)
        self.command = command

        self.indicator = ctk.CTkFrame(self, width=4, height=20, corner_radius=2, fg_color=(LIGHT_COLOR_ACCENT,DARK_COLOR_ACCENT) if is_active else "transparent")
        self.indicator.pack(side="left", padx=(10, 10))

        self.label = ctk.CTkLabel(self, text=text, anchor="w", text_color="white" if is_active else (LIGHT_COLOR_TEXT_SUB,DARK_COLOR_TEXT_SUB), font=("Segoe UI", 14, "bold" if is_active else "normal"))
        self.label.pack(side="left", fill="both", expand=True)

        self.bind("<Button-1>", self.OnClick)
        self.label.bind("<Button-1>", self.OnClick)
        self.indicator.bind("<Button-1>", self.OnClick)

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.indicator.configure(fg_color=(LIGHT_COLOR_ACCENT,DARK_COLOR_ACCENT) if active else "transparent")
        self.label.configure(text_color="white" if active else (LIGHT_COLOR_TEXT_SUB,DARK_COLOR_TEXT_SUB), font=("Segoe UI", 14, "bold" if active else "normal"))

class PIPplayer(ctk.CTkFrame):  
    def __init__(self, master):
        super().__init__(master, width=140, height=140, corner_radius=12, fg_color="#000000", border_width=0)
        self.place(relx=0.96, rely=0.96, anchor="se")
        self.pack_propagate(False)

        self.art = ctk.CTkLabel(self, text="♫", font=("Arial", 60), fg_color="#333333", text_color="#555555")
        self.art.place(relwidth=1, relheight=1)

        self.controls = ctk.CTkFrame(self, height=40, fg_color="#000000", corner_radius=0)
        self.controls.place(relx=0, rely=1.0, relwidth=1, anchor="sw")
        self.controls.configure(fg_color="#1a1a1a")

        self.btn_play = ctk.CTkButton(self.controls, text="▶", width=30, height=30, fg_color=("white","black"), text_color=("white","black"), corner_radius=15)
        self.btn_play.pack(pady=5)

        self.btn_max = ctk.CTkButton(self, text="⤢", width=25, height=25, fg_color="#444444", hover_color="#666666")
        self.btn_close = ctk.CTkButton(self, text="✕", width=25, height=25, fg_color="#AA0000", hover_color="#FF0000")

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.art.bind("<Enter>", self.on_enter)
        self.controls.bind("<Enter>", self.on_enter)

    def on_enter(self, event):
        self.btn_max.place(relx=0.05, rely=0.05, anchor="nw")
        self.btn_close.place(relx=0.95, rely=0.05, anchor="ne")

    def on_leave(self, event):
        self.btn_max.place_forget()
        self.btn_close.place_forget()

class SongRow(ctk.CTkFrame):
    def __init__(self, master, index, title, artist, album, duration):
        super().__init__(master, fg_color="transparent", height=60, corner_radius=6)
        self.pack(fill="x", pady=1)

        self.bind("<Enter>", lambda e: self.configure(fg_color=(LIGHT_COLOR_HOVER,DARK_COLOR_HOVER)))
        self.bind("<Leave>", lambda e: self.configure(fg_color="transparent"))

        self.art = ctk.CTkFrame(self, width=40, height=40, corner_radius=4, fg_color="#333333")
        self.art.pack(side="left", padx=(10, 10))

        ctk.CTkLabel(self, text=title, font=("Segoe UI", 13, "bold"), text_color="white", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkLabel(self, text=artist, width=150, anchor="w", text_color=(LIGHT_COLOR_TEXT_SUB,DARK_COLOR_TEXT_SUB)).pack(side="left", padx=10)
        ctk.CTkLabel(self, text=album, width=150, anchor="w", text_color=(LIGHT_COLOR_TEXT_SUB,DARK_COLOR_TEXT_SUB)).pack(side="left", padx=10)
        ctk.CTkLabel(self, text=duration, width=60, anchor="e", text_color=(LIGHT_COLOR_TEXT_SUB,DARK_COLOR_TEXT_SUB)).pack(side="right", padx=20)

class MyMusic(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkEntry(header, placeholder_text="Search...", height=40, fg_color="#222222", border_width=0, corner_radius=8).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        add_btn = ctk.CTkButton(scroll, text="+  Add Music", height=50, fg_color="#222222", hover_color="#333333", font=("Segoe UI", 14, "bold"), anchor="w")
        add_btn.pack(fill="x", pady=(0, 10))

        data = [
            ("Paranoid Android", "Radiohead", "OK Computer", "6:23"),
            ("Time", "Pink Floyd", "DSOTM", "6:53"),
            ("Starlight", "Muse", "Black Holes", "3:59"),
            ("Money", "Pink Floyd", "DSOTM", "6:22"),
            ("Karma Police", "Radiohead", "OK Computer", "4:21"),
            ("Uprising", "Muse", "The Resistance", "5:03"),
        ]
        for i in range(15):
            s = data[i % len(data)]
            SongRow(scroll, i+1, s[0], s[1], s[2], s[3])

class Playlist(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="PLAYLISTS", font=("Segoe UI", 24, "bold")).pack(pady=40)
        ctk.CTkButton(self, text="+ Create New Playlist", fg_color=(LIGHT_COLOR_ACCENT,DARK_COLOR_ACCENT)).pack()

class History(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        tabs = ctk.CTkSegmentedButton(self, values=["Advanced History", "Recap"])
        tabs.set("Advanced History")
        tabs.pack(fill="x", pady=(0, 20))

        header = ctk.CTkFrame(self, height=30, fg_color="#222222")
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Title", width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Played At", width=150, anchor="w").pack(side="left")
        ctk.CTkLabel(header, text="Duration", width=100, anchor="w").pack(side="left")

        ctk.CTkLabel(self, text="No history yet...", text_color="grey").pack(pady=40)

class Settings(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="SETTINGS", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 20))
        
        row= ctk.CTkFrame(self, fg_color="#222222", height=50)
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text="Music Library Path").pack(side="left", padx=20)
        ctk.CTkOptionMenu(row, values=["System", "Dark", "Light"], width=100, height=23, command=self.change_theme).pack(side="right", padx=20)

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

if __name__ == "__main__":
    main=Main()
    main.mainloop()