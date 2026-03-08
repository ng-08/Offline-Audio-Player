import vlc
import os
import time

class AudioEngine:
    def __init__(self):
        # Fire up the VLC instance and create a blank player
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.current_song = None

    def load_and_play(self, file_path):
        if not os.path.exists(file_path):
            print(f"❌ Error: Could not find file at '{file_path}'")
            return

        try:
            media = self.vlc_instance.media_new(file_path)
            self.player.set_media(media)
            
            self.player.play()
            self.current_song = file_path
            
            time.sleep(0.1) 
            
            print(f"▶️ Now Playing: {os.path.basename(file_path)}")
            
        except Exception as e:
            print(f"❌ Error loading audio: {e}")

    def toggle_play_pause(self):
        if not self.current_song:
            print("⚠️ No song is currently loaded!")
            return

        self.player.pause()
        
        time.sleep(0.05)
        if self.player.is_playing():
            print("▶️ Resumed")
        else:
            print("⏸ Paused")

    def stop(self):
        """Completely kills playback and drops the media."""
        self.player.stop()
        print("⏹ Stopped")

if __name__ == "__main__":
    engine = AudioEngine()
    
    test_song = "" #place test song file path
    
    print("\n--- Audio Engine Sandbox (VLC Powered) ---")
    print("Commands: [p]lay, [t]oggle pause, [s]top, [q]quit")
    
    while True:
        command = input("\nEnter command: ").lower()
        
        if command == 'p':
            engine.load_and_play(test_song)
        elif command == 't':
            engine.toggle_play_pause()
        elif command == 's':
            engine.stop()
        elif command == 'q':
            engine.stop()
            print("Exiting engine...")
            break
        else:
            print("Unknown command.")