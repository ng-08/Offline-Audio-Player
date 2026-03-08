import customtkinter as ctk
import vlc
import os
import sys
from PIL import Image#

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

#color
BGcolor=("#DDDDDD","#121212")
SideBarColor=("#B6B6B6","#1E1E1E")
AccentColor=("#3B8ED0","#3B8ED0")##
SubTextColor=("#4E4E4E","#888888")#
HoverColor=("#D1CECE", "#2B2B2B")
SubBGcolor=("#C0C0C0","#222222")
SubHoverColor=("#979797","#333333")
TextColor=("#000000","#FFFFFF")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
test_song="" #place test song file path
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
        
        self.geometry(f"{AppHeight}x{AppHeight}+{x}+{y}")
        
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.engine=AudioEngine()
        self.engine.load(test_song)

        self.play_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "play.png")), size=(40, 40))
        self.pause_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "pause.png")), size=(40, 40))

        self.btn_play=ctk.CTkButton(self, image=self.pause_img, text="",
                                       fg_color="transparent", command=self.toggle)
        self.btn_play.pack()

    def toggle(self):
        if self.engine.is_playing():
            self.engine.pause()
            self.btn_play.configure(image=self.play_img)
        else:
            self.engine.play()
            self.btn_play.configure(image=self.pause_img)

class AudioEngine:
    def __init__(self):
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.current_song = None

    def load(self, file_path):
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
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

if __name__ == "__main__":
    main=Main()
    main.mainloop()