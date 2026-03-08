import sqlite3
import os
from datetime import datetime
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import random

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
        self.cursor.execute("DELETE FROM Queue")
        self.conn.commit()

        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        TotalSongs=self.cursor.fetchone()[0]

        for i in range(50):
            RandomSong=random.randint(1, TotalSongs)
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (RandomSong,))

        self.conn.commit()

    def ModeNormal(self, table):
        self.cursor.execute("DELETE FROM Queue")
        self.conn.commit()

        self.cursor.execute(f"SELECT SongSno FROM {table}")

        for i in self.cursor.fetchall():
            self.cursor.execute("INSERT INTO Queue (SongSno) VALUES (?)", (i[0]))
        self.conn.commit()

    def Refill(self, mode, table):
        self.cursor.execute("SELECT COUNT(*) FROM Queue WHERE Played = 0")
        Dif=50-self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
        TotalSongs=self.cursor.fetchone()[0]

        if mode == 1:
            for i in range (Dif):
                RandomSong=random.randint(1, TotalSongs)
                self.cursor.execute("INSERT INTO Queue (SongSno) VALUES(?)", (RandomSong,))
    
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

class Playlist:
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

class History:##
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

if __name__=="__main__":
    d=Default()
    d.create_tables()
    db=Database(d.conn, d.cursor)
    db.add_directory("")#place file path
    db.scan()
    db.close()  
