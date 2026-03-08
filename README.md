This is a semi-vibe coded Audio Player, its still in early development, following is a per file discription:-

FNP1 — bare bones VLC audio engine, terminal controlled. Tests loading and playing any audio format, toggle play/pause, stop. No GUI.
FNP2 — first CustomTkinter GUI. Single play/pause button with icon swap, VLC backend wired in. Proof of concept for the UI/audio connection.
FNP3 — major step up. Added next/prev controls, SQLite queue system, database scan for local music, cover art extraction and display, title/artist labels.
FNP4 — isolated progress bar prototype. Tests seek on click, drag to scrub, time labels updating in real time. Built separately before merging into main player.
FNP5 — merged progress bar into main player. Added history recording on track change.
FNP6 — shuffle toggle with queue clear and refill, auto advance to next song on track end via VLC event callback, prev button restart logic (restarts if over 3 seconds in, goes back if under), gap-safe random queue using ORDER BY RANDOM().
FNP7 — current working file. Split Songs table into Songs (file location) and SongData (metadata). Full Metadata class for reading and writing tags across 7 formats (mp3, flac, ogg, wav, m4a, opus, wma). GetCoverArt handles cover extraction per format. has_cover flag added.

DBP1/DBP2 — standalone database prototypes. DBP1 is basic Songs table and scan. DBP2 adds Queue, Display, Playlist, History classes before they were merged into FNP.
UIP1/UIP2/UIP3 — standalone UI prototypes. Sidebar navigation, song rows, PIP player widget, history and settings views. Design iterations before merging into FNP.
