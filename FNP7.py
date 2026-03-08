import io
import os
import vlc
import sys
import base64
import sqlite3
from PIL import Image
from mutagen.asf import ASF
from mutagen.mp4 import MP4
import customtkinter as ctk
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
from datetime import datetime
from mutagen.id3 import ID3, APIC
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC, Picture
from mutagen.oggvorbis import OggVorbis
from mutagen.asf import ASFByteArrayAttribute

#color  ##
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

BGcolor=("#DDDDDD","#121212")
SideBarColor=("#B6B6B6","#1E1E1E")
AccentColor=("#3B8ED0","#3B8ED0")##
SubTextColor=("#4E4E4E","#888888")#
HoverColor=("#D1CECE", "#2B2B2B")
SubBGcolor=("#C0C0C0","#222222")
SubHoverColor=("#979797","#333333")
TextColor=("#000000","#FFFFFF")

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(__file__)

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

class BasicUI(ctk.CTkFrame):#
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

class PlayerInfo:#
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
        self.cursor.execute("SELECT Title FROM SongData WHERE SongSno = ?", (SongSno,))
        Title=self.cursor.fetchone()[0]
        if Title:
            return Title
        else:
            return "N-A"
        
    def GetArtist(self, SongSno):
        self.cursor.execute("SELECT Artist FROM SongData WHERE SongSno = ?", (SongSno,))
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

            elif file_path.lower().endswith('.flac'):
                audio = FLAC(file_path)
                if audio.pictures:
                    cover = Image.open(io.BytesIO(audio.pictures[0].data))

            elif file_path.lower().endswith('.ogg'):
                audio = OggVorbis(file_path)
                if 'metadata_block_picture' in audio:
                    pic = Picture(base64.b64decode(audio['metadata_block_picture'][0]))
                    cover = Image.open(io.BytesIO(pic.data))

            elif file_path.lower().endswith('.wav'):
                audio = WAVE(file_path)
                if audio.tags:
                    for tag in audio.tags.values():
                        if tag.FrameID == 'APIC':
                            cover = Image.open(io.BytesIO(tag.data))

            elif file_path.lower().endswith('.m4a'):
                audio = MP4(file_path)
                if audio.tags and 'covr' in audio.tags:
                    cover = Image.open(io.BytesIO(bytes(audio.tags['covr'][0])))

            elif file_path.lower().endswith('.opus'):
                audio = OggOpus(file_path)
                if 'metadata_block_picture' in audio:
                    pic = Picture(base64.b64decode(audio['metadata_block_picture'][0]))
                    cover = Image.open(io.BytesIO(pic.data))

            elif file_path.lower().endswith('.wma'):
                audio = ASF(file_path)
                if 'WM/Picture' in audio.tags:
                    cover = Image.open(io.BytesIO(bytes(audio.tags['WM/Picture'][0].value)))
            
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Songs (
                SongSno INTEGER PRIMARY KEY AUTOINCREMENT,
                DirSno INTEGER,
                SubPath TEXT,
                SongFileName TEXT,      
                FOREIGN KEY (DirSno) REFERENCES Directories(DirSno)            
            )
        ''')
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS SongData (
                SongSno INTEGER,
                Title TEXT,
                Artist TEXT,
                Album TEXT,
                Duration INTEGER,
                CoverArt TEXT,
                TrackNumber INTEGER,
                Year INTEGER,
                Genre TEXT,
                DateAdded TEXT,
                FOREIGN KEY (SongSno) REFERENCES Songs(SongSno)
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

class Database:#
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def add_directory(self, path):
        self.cursor.execute("INSERT INTO Directories (FilePath) VALUES (?)", (path,))
        self.conn.commit()

    def scan(self):#
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
                            INSERT INTO Songs (DirSno, SubPath, SongFileName)
                            VALUES (?, ?, ?)
                        """, (dirSno, subpath, file,))

                        SongSno=self.cursor.lastrowid

                        self.cursor.execute("""
                            INSERT INTO SongData (SongSno, Title, Artist, Album, Duration, TrackNumber, Year, Genre, DateAdded)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (SongSno, title, artist, album, duration, tracknum, year, genre, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                    except Exception:
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
        
        if mode == 1:
            self.cursor.execute(f"SELECT SongSno FROM {table} ORDER BY RANDOM() LIMIT ?", (Dif,))
            songs=self.cursor.fetchall()
            for song in songs:
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (song[0],))
                
        elif mode == 2:
            self.cursor.execute(f"SELECT SongSno FROM {table}")

            for i in self.cursor.fetchall():
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES (?)", (i[0],))
            
        self.conn.commit()

    def mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 1 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

    def un_mark_played(self, QueueNo):
        self.cursor.execute("UPDATE Queue SET Played = 0 WHERE QueueNo = ?", (QueueNo,))
        self.conn.commit()

class Display:#
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
 
class Metadata:#
    def __init__(self):
        self.format_map = {
            '.mp3':  (self._read_mp3,  self._write_mp3),
            '.flac': (self._read_flac, self._write_flac),
            '.ogg':  (self._read_ogg,  self._write_ogg),
            '.wav':  (self._read_wav,  self._write_wav),
            '.m4a':  (self._read_m4a,  self._write_m4a),
            '.opus': (self._read_opus, self._write_opus),
            '.wma':  (self._read_wma,  self._write_wma),
        }

    def read(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.format_map:
            return {}
        read_func, _ = self.format_map[ext]
        return read_func(file_path)

    def _read_mp3(self, path):
        try:
            tags = EasyID3(path)
            audio = MP3(path, ID3=ID3)
            has_cover = any(tag.FrameID == 'APIC' for tag in audio.tags.values()) if audio.tags else False
            return {
                'title':       tags.get('title',       [''])[0],
                'artist':      tags.get('artist',      [''])[0],
                'album':       tags.get('album',       [''])[0],
                'genre':       tags.get('genre',       [''])[0],
                'year':        tags.get('date',        [''])[0],
                'tracknumber': tags.get('tracknumber', [''])[0],
                'duration':    int(audio.info.length),
                'has_cover':   has_cover,
            }
        except Exception:
            return {}

    def _read_flac(self, path):
        try:
            audio = FLAC(path)
            return {
                'title':       audio.get('title',       [''])[0],
                'artist':      audio.get('artist',      [''])[0],
                'album':       audio.get('album',       [''])[0],
                'genre':       audio.get('genre',       [''])[0],
                'year':        audio.get('date',        [''])[0],
                'tracknumber': audio.get('tracknumber', [''])[0],
                'duration':    int(audio.info.length),
                'has_cover':   bool(audio.pictures),
            }
        except Exception:
            return {}

    def _read_ogg(self, path):
        try:
            audio = OggVorbis(path)
            return {
                'title':       audio.get('title',       [''])[0],
                'artist':      audio.get('artist',      [''])[0],
                'album':       audio.get('album',       [''])[0],
                'genre':       audio.get('genre',       [''])[0],
                'year':        audio.get('date',        [''])[0],
                'tracknumber': audio.get('tracknumber', [''])[0],
                'duration':    int(audio.info.length),
                'has_cover':   'metadata_block_picture' in audio,
            }
        except Exception:
            return {}

    def _read_wav(self, path):
        try:
            audio = WAVE(path)
            tags = audio.tags or {}
            has_cover = any(getattr(t, 'FrameID', '') == 'APIC' for t in tags.values()) if tags else False
            return {
                'title':       str(tags.get('TIT2', '')),
                'artist':      str(tags.get('TPE1', '')),
                'album':       str(tags.get('TALB', '')),
                'genre':       str(tags.get('TCON', '')),
                'year':        str(tags.get('TDRC', '')),
                'tracknumber': str(tags.get('TRCK', '')),
                'duration':    int(audio.info.length),
                'has_cover':   has_cover,
            }
        except Exception:
            return {}

    def _read_m4a(self, path):
        try:
            audio = MP4(path)
            tags = audio.tags or {}
            return {
                'title':       tags.get('\xa9nam', [''])[0],
                'artist':      tags.get('\xa9ART', [''])[0],
                'album':       tags.get('\xa9alb', [''])[0],
                'genre':       tags.get('\xa9gen', [''])[0],
                'year':        tags.get('\xa9day', [''])[0],
                'tracknumber': str(tags.get('trkn', [(0, 0)])[0][0]),
                'duration':    int(audio.info.length),
                'has_cover':   'covr' in tags,
            }
        except Exception:
            return {}

    def _read_opus(self, path):
        try:
            audio = OggOpus(path)
            return {
                'title':       audio.get('title',       [''])[0],
                'artist':      audio.get('artist',      [''])[0],
                'album':       audio.get('album',       [''])[0],
                'genre':       audio.get('genre',       [''])[0],
                'year':        audio.get('date',        [''])[0],
                'tracknumber': audio.get('tracknumber', [''])[0],
                'duration':    int(audio.info.length),
                'has_cover':   'metadata_block_picture' in audio,
            }
        except Exception:
            return {}

    def _read_wma(self, path):
        try:
            audio = ASF(path)
            tags = audio.tags or {}
            return {
                'title':       str(tags.get('Title',          [['']])[0]),
                'artist':      str(tags.get('Author',         [['']])[0]),
                'album':       str(tags.get('WM/AlbumTitle',  [['']])[0]),
                'genre':       str(tags.get('WM/Genre',       [['']])[0]),
                'year':        str(tags.get('WM/Year',        [['']])[0]),
                'tracknumber': str(tags.get('WM/TrackNumber', [['']])[0]),
                'duration':    int(audio.info.length),
                'has_cover':   'WM/Picture' in tags,
            }
        except Exception:
            return {}

    def write(self, file_path, data):
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in self.format_map:
            return False
        _, write_func = self.format_map[ext]
        return write_func(file_path, data)

    def _write_mp3(self, path, data):
        try:
            try:
                tags = EasyID3(path)
            except:
                tags = EasyID3()
                tags.save(path)
                tags = EasyID3(path)

            if 'title'       in data: tags['title']       = data['title']
            if 'artist'      in data: tags['artist']      = data['artist']
            if 'album'       in data: tags['album']       = data['album']
            if 'genre'       in data: tags['genre']       = data['genre']
            if 'year'        in data: tags['date']        = data['year']
            if 'tracknumber' in data: tags['tracknumber'] = data['tracknumber']
            tags.save()

            if 'cover_path' in data:
                full_tags = ID3(path)
                with open(data['cover_path'], 'rb') as img:
                    img_data = img.read()
                mime = 'image/jpeg' if data['cover_path'].endswith('.jpg') or data['cover_path'].endswith('.jpeg') else 'image/png'
                full_tags.delall('APIC')
                full_tags['APIC'] = APIC(encoding=3, mime=mime, type=3, desc='Cover', data=img_data)
                full_tags.save()
            return True
        except Exception:
            return False

    def _write_flac(self, path, data):
        try:
            audio = FLAC(path)
            if 'title'       in data: audio['title']       = data['title']
            if 'artist'      in data: audio['artist']      = data['artist']
            if 'album'       in data: audio['album']       = data['album']
            if 'genre'       in data: audio['genre']       = data['genre']
            if 'year'        in data: audio['date']        = data['year']
            if 'tracknumber' in data: audio['tracknumber'] = data['tracknumber']

            if 'cover_path' in data:
                pic = Picture()
                with open(data['cover_path'], 'rb') as img:
                    pic.data = img.read()
                pic.type = 3
                pic.mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                audio.clear_pictures()
                audio.add_picture(pic)
            audio.save()
            return True
        except Exception:
            return False

    def _write_ogg(self, path, data):
        try:
            audio = OggVorbis(path)
            if 'title'       in data: audio['title']       = data['title']
            if 'artist'      in data: audio['artist']      = data['artist']
            if 'album'       in data: audio['album']       = data['album']
            if 'genre'       in data: audio['genre']       = data['genre']
            if 'year'        in data: audio['date']        = data['year']
            if 'tracknumber' in data: audio['tracknumber'] = data['tracknumber']

            if 'cover_path' in data:
                with open(data['cover_path'], 'rb') as img:
                    img_data = img.read()
                pic = Picture()
                pic.data = img_data
                pic.type = 3
                pic.mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                encoded = base64.b64encode(pic.write()).decode('ascii')
                audio['metadata_block_picture'] = [encoded]
            audio.save()
            return True
        except Exception:
            return False

    def _write_wav(self, path, data):
        try:
            audio = WAVE(path)
            if audio.tags is None:
                audio.add_tags()
            from mutagen.id3 import TIT2, TPE1, TALB, TCON, TDRC, TRCK
            if 'title'       in data: audio.tags['TIT2'] = TIT2(encoding=3, text=data['title'])
            if 'artist'      in data: audio.tags['TPE1'] = TPE1(encoding=3, text=data['artist'])
            if 'album'       in data: audio.tags['TALB'] = TALB(encoding=3, text=data['album'])
            if 'genre'       in data: audio.tags['TCON'] = TCON(encoding=3, text=data['genre'])
            if 'year'        in data: audio.tags['TDRC'] = TDRC(encoding=3, text=data['year'])
            if 'tracknumber' in data: audio.tags['TRCK'] = TRCK(encoding=3, text=data['tracknumber'])

            if 'cover_path' in data:
                with open(data['cover_path'], 'rb') as img:
                    img_data = img.read()
                mime = 'image/jpeg' if data['cover_path'].endswith(('.jpg', '.jpeg')) else 'image/png'
                audio.tags.delall('APIC')
                audio.tags['APIC'] = APIC(encoding=3, mime=mime, type=3, desc='Cover', data=img_data)

            audio.save()
            return True
        except Exception:
            return False

    def _write_m4a(self, path, data):
        try:
            audio = MP4(path)
            if audio.tags is None:
                audio.add_tags()
            if 'title'       in data: audio.tags['\xa9nam'] = [data['title']]
            if 'artist'      in data: audio.tags['\xa9ART'] = [data['artist']]
            if 'album'       in data: audio.tags['\xa9alb'] = [data['album']]
            if 'genre'       in data: audio.tags['\xa9gen'] = [data['genre']]
            if 'year'        in data: audio.tags['\xa9day'] = [data['year']]
            if 'tracknumber' in data:
                audio.tags['trkn'] = [(int(data['tracknumber']), 0)]
            if 'cover_path' in data:
                from mutagen.mp4 import MP4Cover
                with open(data['cover_path'], 'rb') as img:
                    img_data = img.read()
                fmt = MP4Cover.FORMAT_JPEG if data['cover_path'].endswith(('.jpg', '.jpeg')) else MP4Cover.FORMAT_PNG
                audio.tags['covr'] = [MP4Cover(img_data, imageformat=fmt)]
            audio.save()
            return True
        except Exception:
            return False

    def _write_opus(self, path, data):
        try:
            audio = OggOpus(path)
            if 'title'       in data: audio['title']       = data['title']
            if 'artist'      in data: audio['artist']      = data['artist']
            if 'album'       in data: audio['album']       = data['album']
            if 'genre'       in data: audio['genre']       = data['genre']
            if 'year'        in data: audio['date']        = data['year']
            if 'tracknumber' in data: audio['tracknumber'] = data['tracknumber']
            audio.save()
            return True
        except Exception:
            return False

    def _write_wma(self, path, data):
        try:
            audio = ASF(path)
            if 'title'       in data: audio.tags['Title']          = [data['title']]
            if 'artist'      in data: audio.tags['Author']         = [data['artist']]
            if 'album'       in data: audio.tags['WM/AlbumTitle']  = [data['album']]
            if 'genre'       in data: audio.tags['WM/Genre']       = [data['genre']]
            if 'year'        in data: audio.tags['WM/Year']        = [data['year']]
            if 'tracknumber' in data: audio.tags['WM/TrackNumber'] = [data['tracknumber']]
            
            if 'cover_path' in data:
                with open(data['cover_path'], 'rb') as img:
                    img_data = img.read()
                audio.tags['WM/Picture'] = [ASFByteArrayAttribute(img_data)]
            
            audio.save()
            return True
        except Exception:
            return False

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
    db.add_directory("/home/ng8/Music")#place test song directory
    db.scan()#
    q=Queue(d.conn, d.cursor)#
    q.ModeRandom("Songs")
    pi=PlayerInfo(d.conn, d.cursor)
    h=History(d.conn, d.cursor)
    main=Main(pi, db, q, h)
    main.mainloop()

