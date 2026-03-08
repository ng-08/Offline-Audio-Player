import sqlite3
import os
from datetime import datetime
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import random

class Default:
    def __init__(self):
        self.conn = sqlite3.connect("Music.db")
        self.cursor = self.conn.cursor()
    
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
                            INSERT INTO Songs (DirSno, SongFileName, Title, Artist, Album, Duration, TrackNumber, Year, Genre, DateAdded)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (dirSno, file, title, artist, album, duration, tracknum, year, genre, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                    except Exception as e:
                        print(f"Skipped {file}: {e}")
                        continue

        self.conn.commit()
        print("Scan complete")

    def close(self):
        self.conn.close()

class QueueR:
    def __init__(self, conn, cursor):
        self.conn=conn
        self.cursor=cursor

    def make_queue(self):
        self.cursor.execute("SELECT COUNT(*) FROM Queue")
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

class PlaylistDB:

    pass

if __name__=="__main__":
    d=Default()
    d.create_tables()
    db=Database(d.conn, d.cursor)
    db.add_directory("")#place file path
    db.scan()
    db.close()  