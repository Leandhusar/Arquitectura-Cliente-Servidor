import zmq
import os, sys
from pygame import mixer
import io

mixer.init()
socket = zmq.Context().socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

def saveFile(file):
    with open('temporal.mp3', 'wb') as new_file:
        new_file.write(file)
        new_file.close()

def downloadFile(file_name):
    msg = [b'Download', file_name.encode('utf-8')]
    socket.send_multipart(msg)
    msg = socket.recv_multipart()
    if msg[0].decode('utf-8') == 'Ok':
        file_data = msg[1]
        return file_data
    else:
        print(msg[0].decode('utf-8'))
        return False

def getFilesList():
    msg = [b'Listdir']
    socket.send_multipart(msg)
    msg = socket.recv_multipart()
    print('Songs available:')
    msg.pop(0)
    for dir in msg:
        print("- " + dir.decode('utf-8'))

def play(song):
    buffer = downloadFile(song)
    try:
        mixer.music.load(io.BytesIO(buffer))
        mixer.music.set_volume(0.5)
        mixer.music.play()
    except:
        print("Song titled <<{song}>> doesn't exist".format(song))

def pause():
    mixer.music.pause()

def unpause():
    mixer.music.unpause()

def enqueue(songs, song):
    songs.append(song)

def dequeue(songs, song):
    try:
        songs.remove(song)
    except:
        pass

def playNext(songs, position):
    try:
        mixer.music.stop()
        position[0] += 1
        play(songs[position[0]])
    except:
        pass

def playPrev(songs, position):
    try:
        mixer.music.stop()
        position[0] -= 1
        play(songs[position[0]])
    except:
        pass
#-----------------------------------------------------------------------

def showCommands():
    print("\nThese are the commands to use Spotipy:")
    print("list songs: Shows every song from server")
    print("play: plays the current song")
    print("enqueue <song>: Enqueues a song to your playlist")
    print("dequeue <song> Dequeues a song from your playlist")
    print("pause: Pauses the current song")
    print("resume: Resumes the paused song")
    print("prev: Plays the previous song in your playlist")
    print("next: Plays the next song in your playlist\n")

def main():
    showCommands()
    songs = []
    playlist_number = [0]
    enable_play = True

    while True:
        command = input(">>> ")
        
        if command == "list songs":
            getFilesList()
        elif command[0:8] == "enqueue ":
            song = command[8:]
            enqueue(songs, song)
        elif command[0:8] == "dequeue ":
            song = command[8:]
            dequeue(songs, song)
        elif command == "pause":
            pause()
        elif command == "resume":
            unpause()
        elif command == "prev":
            playPrev(songs, playlist_number)
        elif command == "next":
            playNext(songs, playlist_number)
        elif command == "play":
            try:
                play(songs[playlist_number[0]])
            except:
                pass
        elif command == "stop":
            mixer.music.stop()
        elif command == "show playlist":
            print(songs, playlist_number)
        else:
            print("Invalid command")


main()