import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

COLOR_BG = "#121212"
COLOR_SIDEBAR = "#1E1E1E"
COLOR_ACCENT = "#3B8ED0"
COLOR_TEXT_MAIN = "#FFFFFF"
COLOR_TEXT_SUB = "#888888"
COLOR_HOVER = "#2B2B2B"


class SidebarButton(ctk.CTkFrame):
    def __init__(self, master, text, command=None, is_active=False):
        super().__init__(master, fg_color="transparent", height=45, corner_radius=6)
        self.pack(fill="x", pady=2, padx=10)
        self.command = command
        
        self.indicator = ctk.CTkFrame(self, width=4, height=20, corner_radius=2,
                                      fg_color=COLOR_ACCENT if is_active else "transparent")
        self.indicator.pack(side="left", padx=(10, 10))

        self.label = ctk.CTkLabel(self, text=text, anchor="w",
                                  text_color="white" if is_active else COLOR_TEXT_SUB,
                                  font=("Segoe UI", 14, "bold" if is_active else "normal"))
        self.label.pack(side="left", fill="both", expand=True)

        self.bind("<Button-1>", self.on_click)
        self.label.bind("<Button-1>", self.on_click)
        self.indicator.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        if self.command: self.command()

    def set_active(self, active):
        self.indicator.configure(fg_color=COLOR_ACCENT if active else "transparent")
        self.label.configure(text_color="white" if active else COLOR_TEXT_SUB,
                             font=("Segoe UI", 14, "bold" if active else "normal"))

class SongRow(ctk.CTkFrame):
    def __init__(self, master, index, title, artist, album, duration):
        super().__init__(master, fg_color="transparent", height=60, corner_radius=6)
        self.pack(fill="x", pady=1)

        self.bind("<Enter>", lambda e: self.configure(fg_color=COLOR_HOVER))
        self.bind("<Leave>", lambda e: self.configure(fg_color="transparent"))

        self.art = ctk.CTkFrame(self, width=40, height=40, corner_radius=4, fg_color="#333333")
        self.art.pack(side="left", padx=(10, 10))
        
        ctk.CTkLabel(self, text=title, font=("Segoe UI", 13, "bold"), text_color="white", anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        ctk.CTkLabel(self, text=artist, width=150, anchor="w", text_color=COLOR_TEXT_SUB).pack(side="left", padx=10)
        ctk.CTkLabel(self, text=album, width=150, anchor="w", text_color=COLOR_TEXT_SUB).pack(side="left", padx=10)
        ctk.CTkLabel(self, text=duration, width=60, anchor="e", text_color=COLOR_TEXT_SUB).pack(side="right", padx=20)

class AllMusicView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        
        header = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkEntry(header, placeholder_text="Search...", height=40, fg_color="#222222", border_width=0, corner_radius=8).pack(fill="x")

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        add_btn = ctk.CTkButton(scroll, text="+  Add Music", height=50, fg_color="#222222", hover_color="#333333", 
                                font=("Segoe UI", 14, "bold"), anchor="w")
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

class PlaylistView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="PLAYLISTS", font=("Segoe UI", 24, "bold")).pack(pady=40)
        ctk.CTkButton(self, text="+ Create New Playlist", fg_color=COLOR_ACCENT).pack()

class HistoryView(ctk.CTkFrame):
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

class SettingsView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="transparent")
        ctk.CTkLabel(self, text="SETTINGS", font=("Segoe UI", 20, "bold")).pack(anchor="w", pady=(0, 20))
        
        row1 = ctk.CTkFrame(self, fg_color="#222222", height=50)
        row1.pack(fill="x", pady=5)
        ctk.CTkLabel(row1, text="Dark Mode").pack(side="left", padx=20)
        ctk.CTkSwitch(row1, text="").pack(side="right", padx=20)

        row4= ctk.CTkFrame(self, fg_color="#222222", height=50)
        row4.pack(fill="x", pady=5)
        ctk.CTkLabel(row4, text="Music Library Path").pack(side="left", padx=20)
        ctk.CTkOptionMenu(row4, values=["System", "Dark", "Light"], width=100, height=23, command=self.change_theme).pack(side="right", padx=20)

        row2 = ctk.CTkFrame(self, fg_color="#222222", height=50)
        row2.pack(fill="x", pady=5)
        ctk.CTkLabel(row2, text="Music Library Path").pack(side="left", padx=20)
        ctk.CTkButton(row2, text="Change", width=60, height=25).pack(side="right", padx=20)

    def change_theme(self, choice):
        ctk.set_appearance_mode(choice)

class PIPPlayer(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, width=140, height=140, corner_radius=12, fg_color="#000000", border_width=0)
        self.place(relx=0.96, rely=0.96, anchor="se")
        self.pack_propagate(False)

        self.art = ctk.CTkLabel(self, text="♫", font=("Arial", 60), fg_color="#333333", text_color="#555555")
        self.art.place(relwidth=1, relheight=1)

        self.controls = ctk.CTkFrame(self, height=40, fg_color="#000000", corner_radius=0)
        self.controls.place(relx=0, rely=1.0, relwidth=1, anchor="sw")
        self.controls.configure(fg_color="#1a1a1a")

        self.btn_play = ctk.CTkButton(self.controls, text="▶", width=30, height=30, fg_color="white", text_color="black", corner_radius=15)
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

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My Concept Player")
        self.geometry("1100x700")
        self.configure(fg_color=COLOR_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=COLOR_SIDEBAR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.pack_propagate(False)

        ctk.CTkFrame(self.sidebar, height=30, fg_color="transparent").pack()

        self.nav_buttons = {}
        self.add_nav("All Music", AllMusicView)
        self.add_nav("Playlist", PlaylistView)
        self.add_nav("History", HistoryView)
        
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)
        self.add_nav("Settings", SettingsView)
        ctk.CTkFrame(self.sidebar, height=20, fg_color="transparent").pack()

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_area.pack_propagate(False)

        self.frames = {}
        self.current_frame = None
        
        self.show_frame("All Music")

        self.pip = PIPPlayer(self)

    def add_nav(self, name, frame_class):
        btn = SidebarButton(self.sidebar, name, command=lambda n=name: self.show_frame(n))
        btn.pack(side="top" , pady=2, padx=10)
        self.nav_buttons[name] = {"btn": btn, "class": frame_class}

    def show_frame(self, name):
        for n, data in self.nav_buttons.items():
            data["btn"].set_active(n == name)

        if self.current_frame:
            self.current_frame.pack_forget()

        frame_class = self.nav_buttons[name]["class"]
        self.current_frame = frame_class(self.main_area)
        self.current_frame.pack(fill="both", expand=True)

    def build_ui(self):
        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.pack(side="left", fill="y")
        
        self.btn1 = ctk.CTkButton(self.sidebar, text="My Music")
        self.btn1.pack(pady=20)

        self.main_view = ctk.CTkFrame(self)
        self.main_view.pack(side="right", fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()