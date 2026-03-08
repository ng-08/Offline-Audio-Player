import customtkinter as ctk
import tkinter as tk
import vlc

ctk.set_appearance_mode("Dark")

test_song=""#place test song file path

class Main(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x120")
        self.title("Progress Bar Test")
        self.resizable(False, False)
        self.configure(fg_color="#121212")

        self.engine=AudioEngine()
        self.engine.load(test_song)

        self.bar=PlayerBar(self, self.engine)
        self.bar.pack(fill="x", padx=40, pady=35)

class PlayerBar(ctk.CTkFrame):
    def __init__(self, master, engine):
        super().__init__(master, fg_color="transparent")
        self.engine=engine
        self.dragging=False

        self.cur_label=ctk.CTkLabel(self, text="0:00", width=40, text_color="#FFFFFF")
        self.cur_label.pack(side="left")

        self.progress=ctk.CTkProgressBar(self, height=8, progress_color="#3B8ED0", fg_color="#333333")
        self.progress.pack(side="left", fill="x", expand=True, padx=8)
        self.progress.set(0)

        self.dur_label=ctk.CTkLabel(self, text="0:00", width=40, text_color="#FFFFFF")
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

class AudioEngine:
    def __init__(self):
        self.vlc_instance=vlc.Instance()
        self.player=self.vlc_instance.media_player_new()

    def load(self, file_path):
        media=self.vlc_instance.media_new(file_path)
        self.player.set_media(media)
        self.player.play()

if __name__=="__main__":
    main=Main()
    main.mainloop()