import io
import os
import vlc
import sys
import sqlite3
from PIL import Image
import customtkinter as ctk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from datetime import datetime
from mutagen.easyid3 import EasyID3


ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#color  ##
BGcolor=("#DDDDDD","#121212")
SideBarColor=("#B6B6B6","#1E1E1E")
AccentColor=("#3B8ED0","#3B8ED0")##
SubTextColor=("#4E4E4E","#888888")#
HoverColor=("#D1CECE", "#2B2B2B")
SubBGcolor=("#C0C0C0","#222222")
SubHoverColor=("#979797","#333333")
TextColor=("#000000","#FFFFFF")


#code
class Main(ctk.CTk):
    def __init__(self, pi, db, q, h):
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

        self.Basic_UI=BasicUI(self, pi, q, h)
        self.Basic_UI.grid(row=0, column=0, sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.ForceClose)

    def ForceClose(self):
        self.db.close()
        self.destroy()
        sys.exit(0)

class BasicUI(ctk.CTkFrame):####
    def __init__(self, master, pi, q, h):
        super().__init__(master)
        self.configure(fg_color=BGcolor)
        self.q=q

        self.h=h

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.pi=pi
        self.engine=AudioEngine()
        self.engine.load(self.pi.GetDirCsong())
        
        self.play_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "play.png")), size=(40, 40))
        self.pause_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "pause.png")), size=(40, 40))
        self.next_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "next.png")), size=(40,40))
        self.prev_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "prev.png")), size=(40,40))
        self.shuffle_img=ctk.CTkImage(Image.open(os.path.join(BASE_DIR, "assets", "shuffle.png")), size=(40,40))

        ctk.CTkFrame(self, height=50, fg_color="transparent").pack()

        self.cover_img=ctk.CTkImage(self.pi.GetCoverArt(self.pi.GetDirCsong()), size=(300, 300))
        self.cover_label=ctk.CTkLabel(self, image=self.cover_img, text="")
        self.cover_label.pack(pady=(40, 10))

        ctk.CTkFrame(self, height=50, fg_color="transparent").pack()

        self.title_label=ctk.CTkLabel(self, text=pi.GetTitle(pi.GetCsong()), font=("Segoe UI", 20, "bold"), text_color=TextColor)
        self.title_label.pack()
        self.artist_label=ctk.CTkLabel(self, text=pi.GetArtist(pi.GetCsong()), font=("Segoe UI", 14), text_color=SubTextColor)
        self.artist_label.pack(pady=(2, 20))

        ctk.CTkFrame(self, height=30, fg_color="transparent").pack(fill="both", expand=True)

        self.bar=PlayerBar(self, self.engine)
        self.bar.pack(fill="x", padx=40)

        controls=ctk.CTkFrame(self, fg_color="transparent")
        controls.pack()

        self.btn_shuffle=ctk.CTkButton(controls, image=self.shuffle_img, text="", width=50, height=50, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.ToggleShuffle)
        self.btn_shuffle.pack(side="left")

        self.btn_prev=ctk.CTkButton(controls, image=self.prev_img, text="", width=50, height=50, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.TogglePrev)
        self.btn_prev.pack(side="left", padx=10)

        self.btn_play=ctk.CTkButton(controls, image=self.pause_img, text="", width=60, height=60, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.TogglePP)
        self.btn_play.pack(side="left", padx=10)

        self.btn_next=ctk.CTkButton(controls, image=self.next_img, text="", width=50, height=50, fg_color="transparent", hover_color=HoverColor, corner_radius=30, command=self.ToggleNext)
        self.btn_next.pack(side="left", padx=10)

        ctk.CTkFrame(self, height=20, fg_color="transparent").pack()

        self.engine.set_end_callback(lambda: self.after(100, self.ToggleNext))

        self.shuffle = False

    def TogglePP(self):
        if self.engine.is_playing():
            self.engine.pause()
            self.btn_play.configure(image=self.play_img)
        else:
            self.engine.play()
            self.btn_play.configure(image=self.pause_img)

    def ToggleShuffle(self):###
        self.shuffle = not self.shuffle
        if self.shuffle:
            self.q.ModeRandom("Songs")
            self.btn_shuffle.configure(fg_color=SubHoverColor)
        else:
            self.q.ModeNormal("Songs", self.pi.GetCsong())
            self.btn_shuffle.configure(fg_color="transparent")
    
    def ToggleNext(self):###
        self.q.mark_played(self.pi.GetCQueueNo())

        self.h.RecHistory(self.pi.GetCsong())
        
        HNo=self.h.cursor.lastrowid
        self.h.RecDuration(self.engine.player.get_time(), HNo)
        
        Dir=self.pi.GetDirCsong()
        CS=self.pi.GetCsong()

        self.engine.load(Dir)
        self.title_label.configure(text=self.pi.GetTitle(CS))
        self.artist_label.configure(text=self.pi.GetArtist(CS))
        self.cover_img=ctk.CTkImage(self.pi.GetCoverArt(Dir), size=(300, 300))
        self.cover_label.configure(image=self.cover_img)

        self.q.Refill(1, "Songs")

    def TogglePrev(self):###
        pos=self.engine.player.get_time()
        if pos>3000:
            self.engine.player.set_time(0)
        else:
            self.h.RecHistory(self.pi.GetCsong())
        
            HNo=self.h.cursor.lastrowid
            self.h.RecDuration(self.engine.player.get_time(), HNo)

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
        
    def GetCoverArt(self, file_path):#
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

class PlayerBar(ctk.CTkFrame):
    def __init__(self, master, engine):
        super().__init__(master, fg_color="transparent")
        self.engine=engine
        self.dragging=False

        self.cur_label=ctk.CTkLabel(self, text="0:00", width=40, text_color=TextColor)
        self.cur_label.pack(side="left")

        self.progress=ctk.CTkProgressBar(self, height=8, progress_color=TextColor, fg_color=SubBGcolor)
        self.progress.pack(side="left", fill="x", expand=True, padx=8)
        self.progress.set(0)

        self.dur_label=ctk.CTkLabel(self, text="0:00", width=40, text_color=TextColor)
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS History (
                HistoryNo INTEGER PRIMARY KEY AUTOINCREMENT,
                SongSno INTEGER,
                DatePlayed TEXT,
                DurationPlayed INTEGER,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Playlist (
                PlaylistSno INTEGER PRIMARY KEY AUTOINCREMENT,
                PlaylistName TEXT,
                DateCreated TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Display (
                Sno INTEGER PRIMARY KEY,
                SongSno INTEGER,
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
                        continue

        self.conn.commit()

    def close(self):
        self.conn.close()

class Queue:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def ModeRandom(self, table):
        self.cursor.execute("DELETE FROM Queue WHERE Played = 0")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY RANDOM() LIMIT 30")
        songs=self.cursor.fetchall()
        for song in songs:
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (song[0],))

        self.conn.commit()

    def ModeNormal(self, table, CurrentSno):
        self.cursor.execute("DELETE FROM Queue WHERE Played = 0")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table} WHERE SongSno > ? ORDER BY SongSno", (CurrentSno,))
        
        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES (?)",(i[0],))
        self.conn.commit()

    def Refill(self, mode, table):
        self.cursor.execute("SELECT COUNT(*) FROM Queue WHERE Played = 0")
        Dif=20-self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        
        if mode == 1:
            self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY RANDOM() LIMIT ?", (Dif,))
            songs=self.cursor.fetchall()
            for song in songs:
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (song[0],))
                
        elif mode == 2:
            self.cursor.execute(f"SELECT SongSno FROM {table}")

            for i in self.cursor.fetchall():
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES (?)", (i[0]))
            
        self.conn.commit()

    def mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 1 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

    def un_mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 0 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

class Display:##
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def Filter(self, table, metric, order):
        self.cursor.execute("DELETE FROM Display")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY {metric} {order}")

        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Display (SongSno) VALUES (?)", (i[0]))
        self.conn.commit()

    def Search(self, table, querry):
        self.cursor.execute("DELETE FROM Display")
        self.conn.commit()

        self.cursor.execute(f'''SELECT SongSno FROM {table} 
                                WHERE Title LIKE ? OR Artist LIKE ? OR Album LIKE ? OR Genre LIKE ?    
                            ''', (f'%{querry}%', f'%{querry}%', f'%{querry}%', f'%{querry}%'))
        
        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Display (SongSno) VALUES (?)", (i[0]))
        self.conn.commit()

    def Populate(self,table):
        self.cursor.execute("DELETE FROM Display")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table}")

        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Display (SongSno) VALUES (?)", (i[0]))
        self.conn.commit()

class Playlist:###
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def CreatePlaylist(self, placeholder_name):
        self.cursor.execute("SELECT COUNT(*) FROM Playlist WHERE PlaylistName = ?", (placeholder_name,))
        if self.cursor.fetchone()[0] > 0:
            print("Playlist already exists")
            return
        
        else:
            self.cursor.execute(f'''
            CREATE TABLE `{placeholder_name}` (
                Sno INTEGER PRIMARY KEY AUTOINCREMENT,
                SongSno INTEGER,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno) 
            )
            ''')

            self.cursor.execute('''
            INSERT INTO Playlist (PlaylistName, DateCreated)
            VALUES (?, ?)
            ''', (placeholder_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
            self.conn.commit()

    def DeletePlaylist(self, PlaylistSno):
        self.cursor.execute("SELECT COUNT(*) FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        if self.cursor.fetchone()[0] > 0:
            self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
            TabName=self.cursor.fetchone()[0]
            self.cursor.execute(f"DROP TABLE `{TabName}`")
            self.cursor.execute("DELETE FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
            
            self.conn.commit()

        else:
            pass

    def RenamePlaylist(self, PlaylistSno, NewName):
        self.cursor.execute("SELECT COUNT(*) FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        if self.cursor.fetchone()[0] > 0:
            self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
            OldName=self.cursor.fetchone()[0]
            self.cursor.execute("UPDATE Playlist SET PlaylistName = ? WHERE PlaylistSno = ?", (NewName, PlaylistSno,))
            self.cursor.execute(f"ALTER TABLE `{OldName}` RENAME TO `{NewName}`")

            self.conn.commit()

        else:
            pass

    def AddSong(self, PlaylistSno, SongSno):
        self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        x=self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM `{x}` WHERE SongSno = ?", (SongSno,))
        if self.cursor.fetchone()[0]==0:
            self.cursor.execute(f"INSERT INTO `{x}`(SongSno) VALUES(?)", (SongSno,))

            self.conn.commit()

        else:
            pass

    def RemoveSong(self, PlaylistSno, SongSno):
        self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        x=self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM `{x}` WHERE SongSno = ?", (SongSno,))
        if self.cursor.fetchone()[0]>0:
            self.cursor.execute(f"DELETE FROM `{x}` WHERE SongSno = ?", (SongSno,))

            self.conn.commit()

        else:
            pass

    def GetSongs(self, PlaylistSno):
        self.cursor.execute("SELECT PlaylistName FROM Playlist WHERE PlaylistSno = ?", (PlaylistSno,))
        x=self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT * FROM `{x}`")
        return self.cursor.fetchall()

    def GetAllPlaylists(self):
        self.cursor.execute("SELECT PlaylistName FROM Playlist")
        return self.cursor.fetchall()

class History:###
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def RecHistory(self, SongSno):
        self.cursor.execute('''
        INSERT INTO History (SongSno, DatePlayed)
        VALUES (?, ?)
        ''', (SongSno, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

        self.conn.commit()

    def RecDuration(self, duration, HNo):
        self.cursor.execute("UPDATE History SET DurationPlayed = ? WHERE HistoryNo = ?", (duration, HNo,))

        self.conn.commit()

    def GetHistory(self):
        self.cursor.execute("SELECT * FROM History")
        return self.cursor.fetchall()

    def ClearHistory(self):
        self.cursor.execute("DELETE FROM History")
        self.conn.commit()

class AudioEngine:
    def __init__(self):
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.current_song = None
        self.events=self.player.event_manager()
        self.events.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_end)
        self._on_end_callback=None

    def load(self, file_path):
        if not os.path.exists(file_path):
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

    def _on_end(self, event):
        if self._on_end_callback:
            self._on_end_callback()

    def set_end_callback(self, callback):
        self._on_end_callback=callback

if __name__=="__main__":
    d=Default()#
    d.create_tables()#
    db=Database(d.conn, d.cursor)
    db.add_directory("")#place test song directory
    db.scan()#
    q=Queue(d.conn, d.cursor)#
    pi=PlayerInfo(d.conn, d.cursor)
    h=History(d.conn, d.cursor)
    main=Main(pi, db, q, h)
    main.mainloop()
