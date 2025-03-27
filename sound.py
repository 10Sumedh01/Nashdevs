import pygame 

# Initialize the mixer before any sound is loaded
pygame.mixer.init()

audio_folder_location = "assets/sound/"
sound_effects = {}
audio_enabled = True

class Sound:
    def __init__(self, file, volume=1.0):
        self.file = file
        if file not in sound_effects:
            path = audio_folder_location + file
            sound_effects[file] = pygame.mixer.Sound(path)
        
        self.sound = sound_effects[file]
        self.sound.set_volume(volume)
        self.channel = None  # Store the channel playing the sound

    def play(self):
        """Plays the sound once."""
        if audio_enabled:
            self.channel = pygame.mixer.Sound.play(self.sound)

    def play_loop(self):
        """Plays the sound in a loop indefinitely."""
        if audio_enabled:
            self.channel = pygame.mixer.Sound.play(self.sound, loops=-1)

    def stop(self):
        """Stops the currently playing sound."""
        if self.channel:
            self.channel.stop()

    def set_volume(self, volume):
        """Sets the volume for this specific sound (0.0 to 1.0)."""
        self.sound.set_volume(volume)

    def pause(self):
        """Pauses the sound if it's playing."""
        if self.channel and self.channel.get_busy():
            self.channel.pause()

    def resume(self):
        """Resumes the paused sound."""
        if self.channel:
            self.channel.unpause()
