import customtkinter as ctk
import vlc
import os
import sys
from PIL import Image
import sqlite3
from datetime import datetime
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import random
from mutagen.id3 import ID3
import io

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

#code
class Main(ctk.CTk):
    def __init__(self, pi, db, q):
        super().__init__()
        self.title("Music Player")
        
        self.db=db

        ScreenWidth=self.winfo_screenwidth()
        ScreenHeight=self.winfo_screenheight()

        AppWidth=int(ScreenWidth*0.70)
        AppHeight=int(ScreenHeight*0.70)
        x=(ScreenWidth//2)-(AppWidth//2)
        y=(ScreenHeight//2)-(AppHeight//2)
        
        self.geometry(f"{AppHeight}x{AppHeight}+{x}+{y}")
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.Basic_UI=BasicUI(self, pi, q)
        self.Basic_UI.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.ForceClose)

    def ForceClose(self):
        self.db.close()
        self.destroy()
        sys.exit(0)

class BasicUI(ctk.CTkFrame):
    def __init__(self, master, pi, q):
        super().__init__(master)
        self.configure(fg_color=BGcolor)
        self.q=q

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.pi=pi
        self.engine=AudioEngine()
        self.engine.load(self.pi.GetDirCsong())

        self.play_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "play.png")), size=(40, 40))
        self.pause_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "pause.png")), size=(40, 40))
        self.next_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "next.png")), size=(40,40))
        self.prev_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "prev.png")), size=(40,40))

        self.cover_img=ctk.CTkImage(self.pi.GetCoverArt(self.pi.GetDirCsong()), size=(300, 300))
        self.cover_label=ctk.CTkLabel(self, image=self.cover_img, text="")
        self.cover_label.pack(pady=(40, 10))

        self.title_label=ctk.CTkLabel(self, text=pi.GetTitle(pi.GetCsong()), font=("Segoe UI", 20, "bold"), text_color=TextColor)
        self.title_label.pack()
        self.artist_label=ctk.CTkLabel(self, text=pi.GetArtist(pi.GetCsong()), font=("Segoe UI", 14), text_color=SubTextColor)
        self.artist_label.pack(pady=(2, 20))

        controls=ctk.CTkFrame(self, fg_color="transparent")
        controls.pack()

        self.btn_prev=ctk.CTkButton(controls, image=self.prev_img, text="", width=50, height=50, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.TogglePrev)
        self.btn_prev.pack(side="left", padx=10)

        self.btn_play=ctk.CTkButton(controls, image=self.pause_img, text="", width=60, height=60, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.TogglePP)
        self.btn_play.pack(side="left", padx=10)

        self.btn_next=ctk.CTkButton(controls, image=self.next_img, text="", width=50, height=50, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.ToggleNext)
        self.btn_next.pack(side="left", padx=10)

    def TogglePP(self):
        if self.engine.is_playing():
            self.engine.pause()
            self.btn_play.configure(image=self.play_img)
        else:
            self.engine.play()
            self.btn_play.configure(image=self.pause_img)

    def ToggleNext(self):
        self.q.mark_played(self.pi.GetCQueueNo())

        Dir=self.pi.GetDirCsong()
        CS=self.pi.GetCsong()

        self.engine.load(Dir)
        self.title_label.configure(text=self.pi.GetTitle(CS))
        self.artist_label.configure(text=self.pi.GetArtist(CS))
        self.cover_img=ctk.CTkImage(self.pi.GetCoverArt(Dir), size=(300, 300))
        self.cover_label.configure(image=self.cover_img)

    def TogglePrev(self):
        self.q.un_mark_played(self.pi.GetCQueueNo()-1)

        Dir=self.pi.GetDirCsong()
        CS=self.pi.GetCsong()

        self.engine.load(Dir)
        self.title_label.configure(text=self.pi.GetTitle(CS))
        self.artist_label.configure(text=self.pi.GetArtist(CS))
        self.cover_img=ctk.CTkImage(self.pi.GetCoverArt(Dir), size=(300, 300))
        self.cover_label.configure(image=self.cover_img)

class PlayerInfo:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def GetCsong(self):
        self.cursor.execute("SELECT SongSno FROM Queue WHERE Played = 0 ORDER BY QueueNo Limit 1")
        return self.cursor.fetchone()[0]

    def GetCQueueNo(self):
        self.cursor.execute("SELECT QueueNo FROM Queue WHERE Played=0 ORDER BY QueueNo LIMIT 1")
        return self.cursor.fetchone()[0]

    def GetDirCsong(self):
        CSNo=self.GetCsong()
        self.cursor.execute("SELECT DirSno FROM Songs WHERE SongSno = ?", (CSNo,))
        CSDirNo=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT FilePath FROM Directories WHERE DirSno = ?", (CSDirNo,))
        CSDirFP=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SongFileName FROM Songs WHERE SongSno = ?", (CSNo,))
        CSSFN=self.cursor.fetchone()[0]
        self.cursor.execute("SELECT SubPath FROM Songs WHERE SongSno = ?", (CSNo,))
        CSSP=self.cursor.fetchone()[0]
        if CSSP:
            return f"{CSDirFP}/{CSSP}/{CSSFN}"
        else:
            return f"{CSDirFP}/{CSSFN}"

    def GetTitle(self, SongSno):
        self.cursor.execute("SELECT Title FROM Songs WHERE SongSno = ?", (SongSno,))
        Title=self.cursor.fetchone()[0]
        if Title:
            return Title
        else:
            return "N-A"
        
    def GetArtist(self, SongSno):
        self.cursor.execute("SELECT Artist FROM Songs WHERE SongSno = ?", (SongSno,))
        Artist=self.cursor.fetchone()[0]
        if Artist:
            return Artist
        else:
            return "N-A"
        
    def GetCoverArt(self, file_path):
        cover=Image.new("RGB", (300, 300), color=(40, 40, 40))
        try:
            if file_path.lower().endswith('.mp3'):
                tags=MP3(file_path, ID3=ID3)
                for tag in tags.values():
                    if tag.FrameID=='APIC':
                        cover=Image.open(io.BytesIO(tag.data))
            else:
                from mutagen import File
                audio=File(file_path)
                if audio and audio.pictures:
                    cover=Image.open(io.BytesIO(audio.pictures[0].data))
        except:
            pass
                    
        return cover

class Default:
    def __init__(self):
        self.conn=sqlite3.connect("Music.db")
        self.cursor=self.conn.cursor()
    
    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Directories (
                DirSno INTEGER PRIMARY KEY AUTOINCREMENT,
                FilePath TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Songs (
                SongSno INTEGER PRIMARY KEY AUTOINCREMENT,
                DirSno INTEGER,
                SubPath TEXT,
                SongFileName TEXT,
                Title TEXT,
                Artist TEXT,
                Album TEXT,
                Duration INTEGER,
                CoverArt TEXT,
                TrackNumber INTEGER,
                Year INTEGER,
                Genre TEXT,
                DateAdded TEXT,
                FOREIGN KEY (DirSno) REFERENCES Directories(DirSno)
            )
        """)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Queue (
                QueueNo INTEGER PRIMARY KEY AUTOINCREMENT,
                SongSno INTEGER,
                Played INTEGER DEFAULT 0,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
            )
        ''')
        self.conn.commit()

class Database:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def add_directory(self, path):
        self.cursor.execute("INSERT INTO Directories (FilePath) VALUES (?)", (path,))
        self.conn.commit()

    def scan(self):
        self.cursor.execute("SELECT DirSno, FilePath FROM Directories")
        dirs = self.cursor.fetchall()

        for dirSno, dirPath in dirs:
            for root, d, files in os.walk(dirPath):
                for file in files:
                    relative_path=os.path.relpath(root, dirPath)
                    subpath="" if relative_path=="." else relative_path
                    filePath=os.path.join(root, file)
                    try:
                        if filePath.lower().endswith('.mp3'):
                            tags=EasyID3(filePath)
                            duration=int(MP3(filePath).info.length)
                        else:
                            from mutagen import File
                            audio=File(filePath)
                            if audio is None:
                                continue
                            tags=audio.tags
                            duration=int(audio.info.length) if audio.info else 0

                        title=str(tags.get("title", [file])[0]) if tags else file
                        artist=str(tags.get("artist", [""])[0]) if tags else ""
                        album=str(tags.get("album", [""])[0]) if tags else ""
                        genre=str(tags.get("genre", [""])[0]) if tags else ""
                        year=str(tags.get("date", [""])[0]) if tags else ""
                        tracknum=str(tags.get("tracknumber", [""])[0]) if tags else ""

                        self.cursor.execute("""
                            INSERT INTO Songs (DirSno, SubPath, SongFileName, Title, Artist, Album, Duration, TrackNumber, Year, Genre, DateAdded)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (dirSno, subpath, file, title, artist, album, duration, tracknum, year, genre, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                    except Exception as e:
                        print(f"Skipped {file}: {e}")
                        continue

        self.conn.commit()
        print("Scan complete")

    def close(self):
        self.conn.close()

class QueueR:##
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def make_queue(self):
        self.cursor.execute("SELECT COUNT(*) FROM Songs")
        TotalSongs=self.cursor.fetchone()[0]

        for i in range(50):
            RandomSong=random.randint(1, TotalSongs)
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (RandomSong,))

        self.conn.commit()

    def mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 1 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

    def un_mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 0 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

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

if __name__=="__main__":
    d=Default()#
    d.create_tables()#
    db=Database(d.conn, d.cursor)
    db.add_directory("")#place test song directory
    db.scan()#
    q=QueueR(d.conn, d.cursor)#
    q.make_queue()#
    pi=PlayerInfo(d.conn, d.cursor)
    main=Main(pi, db, q)
    main.mainloop()