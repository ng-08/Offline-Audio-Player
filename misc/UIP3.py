#modules
import customtkinter as ctk
import sys

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

#color
BGcolor=("#E6E6E6","#121212")
SideBarColor=("#D8D8D8","#1E1E1E")
AccentColor=("#3B8ED0","#3B8ED0")##
SubTextColor=("#4E4E4E","#888888")#
HoverColor=("#D1CECE", "#2B2B2B")
SubBGcolor=("#C0C0C0","#222222")
SubHoverColor=("#979797","#333333")
TextColor=("#000000","#FFFFFF")

#code
class SongRow(ctk.CTkFrame):##
     def __init__(self, master, index, title, artist, album, duration):
        super().__init__(master, fg_color="transparent", height=60, corner_radius=6)
        self.pack(fill="x", pady=1)

        self.bind("<Enter>", lambda e: self.configure(fg_color=HoverColor))
        self.bind("<Leave>", lambda e: self.configure(fg_color="transparent"))

        self.art = ctk.CTkFrame(self, width=40, height=40, corner_radius=4, fg_color=SubHoverColor)
        self.art.pack(side="left", padx=(10, 10), pady=6)

        ctk.CTkLabel(self, text=title, font=("Segoe UI", 15, "bold"), text_color=TextColor, anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkLabel(self, text=artist, width=150, anchor="w", text_color=SubTextColor).pack(side="left", padx=10)
        ctk.CTkLabel(self, text=album, width=150, anchor="w", text_color=SubTextColor).pack(side="left", padx=10)
        ctk.CTkLabel(self, text=duration, width=60, anchor="e", text_color=SubTextColor).pack(side="right", padx=20)

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

        '''self.Def=Default(self)
        self.Def.grid(row=0, column=0, sticky="nsew")'''

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
        self.AddNav("All Music", MyMusic)
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
        
        '''self.PIPp=PIPplayer(self)'''

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

        self.label=ctk.CTkLabel(self, text=text, anchor="w", text_color=TextColor if is_active else SubTextColor, font=("Segoe UI", 18, "bold" if is_active else "normal"))
        self.label.pack(side="left", fill="both", expand=True)

        self.bind("<Button-1>", self.OnClick)
        self.label.bind("<Button-1>", self.OnClick)
        self.indicator.bind("<Button-1>", self.OnClick)

    def OnClick(self, event):
        if self.command: self.command()

    def SetActive(self, active):
        self.indicator.configure(fg_color=AccentColor if active else "transparent")
        self.label.configure(text_color=TextColor if active else SubTextColor, font=("Segoe UI", 20, "bold" if active else "normal"))

class MyMusic(ctk.CTkFrame):##
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        header=ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkEntry(header, placeholder_text="Search...", placeholder_text_color=SubTextColor, text_color=SubTextColor, height=40, fg_color=SubBGcolor, border_width=0, corner_radius=8).pack(fill="x")

        scroll=ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        add_btn=ctk.CTkButton(scroll, text="+  Add Music", height=35, fg_color=SubBGcolor, hover_color=SubHoverColor, text_color=SubTextColor, font=("Segoe UI", 14, "bold"), anchor="w")
        add_btn.pack(fill="x", pady=(0, 10))

        data=[
            ("Paranoid Android", "Radiohead", "OK Computer", "6:23"),
            ("Time", "Pink Floyd", "DSOTM", "6:53"),
            ("Starlight", "Muse", "Black Holes", "3:59"),
            ("Money", "Pink Floyd", "DSOTM", "6:22"),
            ("Karma Police", "Radiohead", "OK Computer", "4:21"),
            ("Uprising", "Muse", "The Resistance", "5:03"),
        ]
        for i in range(15):
            s=data[i % len(data)]
            SongRow(scroll, i+1, s[0], s[1], s[2], s[3])

class Playlist(ctk.CTkFrame):##
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="PLAYLISTS", font=("Segoe UI", 24, "bold")).pack(pady=40)
        ctk.CTkButton(self, text="+ Create New Playlist", fg_color=AccentColor).pack()

class History(ctk.CTkFrame):##
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        self.TabBG=ctk.CTkFrame(self, fg_color=HoverColor, corner_radius=6)
        self.TabBG.pack(fill="x", pady=(0, 20))

        self.TabBG.grid_columnconfigure((0, 1), weight=1)
        self.TabBG.grid_rowconfigure(0, weight=1)

        self.History=ctk.CTkButton(self.TabBG, text="History", fg_color="transparent", hover_color=SubHoverColor, text_color=SubTextColor , corner_radius=6)
        self.History.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)

        self.Recap=ctk.CTkButton(self.TabBG, text="Recap", fg_color=SubBGcolor, hover_color=SubHoverColor, text_color=SubTextColor, corner_radius=6)
        self.Recap.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

class SubHistory(ctk.CTkFrame):##
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        header=ctk.CTkFrame(self, height=30, fg_color=SubBGcolor)
        header.pack(fill="x")
        ctk.CTkLabel(header, text="Title", width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="Played At", width=150, anchor="w").pack(side="left")
        ctk.CTkLabel(header, text="Duration", width=100, anchor="w").pack(side="left")

        ctk.CTkLabel(self, text="No history yet...", text_color=SubTextColor).pack(pady=40)

class Recap(ctk.CTkFrame):##
    pass

class Settings(ctk.CTkFrame):##
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="SETTINGS", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 20))
        
        row=ctk.CTkFrame(self, fg_color=SubBGcolor, height=50)
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text="Theme").pack(side="left", padx=20)
        ctk.CTkOptionMenu(row, values=["System", "Dark", "Light"], width=100, height=23, command=self.change_theme).pack(side="right", padx=20)

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

if __name__=="__main__":
    main=Main()
    main.mainloop()