import pygame
import io

pygame.mixer.init()
pygame.display.init()

screen = pygame.display.set_mode ( ( 320 , 240 ) )

c1 = io.BytesIO(open("Files/Sinister Rouge.mp3", "rb").read())
c2 = io.BytesIO(open("Files/Hello.mp3", "rb").read())
c3 = io.BytesIO(open("Files/Bullet In The Head.mp3", "rb").read())

playlist = list()

playlist.append(c1)
playlist.append(c2)
playlist.append(c3)

pygame.mixer.music.load(playlist.pop(0))      # Get the first track from the playlist
pygame.mixer.music.queue(playlist.pop(0))     # Queue the 2nd song
pygame.mixer.music.set_endevent(pygame.USEREVENT)    # Setup the end track event
pygame.mixer.music.play()                       # Play the music

running = True
while running:
 for event in pygame.event.get():
  if event.type == pygame.USEREVENT:        # A track has ended
   if len ( playlist ) > 0:               # If there are more tracks in the queue...
      pygame.mixer.music.queue(playlist.pop(0)) # Queue the next one in the list