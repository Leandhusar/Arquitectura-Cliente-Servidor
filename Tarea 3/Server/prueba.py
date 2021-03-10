from pygame import mixer, USEREVENT, event, display
import io

mixer.init()
display.init()

c1 = io.BytesIO(open("Files/Hello.mp3", "rb").read())
c2 = io.BytesIO(open("Files/Hello.mp3", "rb").read())
c3 = io.BytesIO(open("Files/Bullet In The Head.mp3", "rb").read())

playlist = list()

playlist.append(c1)
playlist.append(c2)
playlist.append(c3)

MUSIC_END = USEREVENT + 1

def play():
    mixer.music.stop()
    try:
        mixer.music.load(playlist[0])
        mixer.music.set_endevent(MUSIC_END)
        mixer.music.play()

        while len(playlist) > 0:
            for e in event.get():
                if e.type == MUSIC_END:
                    globals()['playlist'].pop(0)
                    mixer.music.load(playlist[0])
                    mixer.music.play()
    except:
        pass

play()