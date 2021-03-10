import threading
import time
import random
import queue
import zmq
import os, sys
from pygame import mixer, USEREVENT, event, display
import io

display.init()
MUSIC_END = USEREVENT + 1
interrupted = False

#Setting socket and connection to server
socket = zmq.Context().socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

#Initialize music mixer
mixer.init()

command = ""
attended_task = True
q = queue.Queue()
q_data = []

#this list contains each playlist created by user
playlist_list = []
data_playlist_list = []
playlist_index = 0
selected = 0

#-------------------------------- functions ---------------------------------------

#obtains the list of songs hosted on the server and prints them on the screen
def getFilesList():
    msg = [b'Listdir']
    socket.send_multipart(msg)
    msg = socket.recv_multipart()
    print('Songs available:')
    msg.pop(0)
    for dir in msg:
        print("- " + dir.decode('utf-8'))

#requests the data of a song and obtains them in pieces
#until its download is complete
def loadSongBytes(file_name):
    try:
        song_bytes = ''
        pointer = 0
        msg = [b'Size', file_name.encode('utf-8')]
        socket.send_multipart(msg)
        msg = socket.recv_multipart()
        song_size = int.from_bytes(msg[1], 'big')

        while pointer < song_size:
            msg = [b'Get Chunk', file_name.encode('utf-8'), pointer.to_bytes(4, 'big')]
            socket.send_multipart(msg)
            msg = socket.recv_multipart()
            chunk_bytes = msg[1].decode('iso-8859-1')
            song_bytes += chunk_bytes
            pointer += 100000

        song_bytes = song_bytes.encode('iso-8859-1')
        return song_bytes
    except:
        return b''

def play():
    mixer.music.load(q_data[0])
    mixer.music.set_endevent(MUSIC_END)
    globals()['q_data'].pop(0)
    q.get()
    mixer.music.play()

#----------------------------------------------------------------------------------


class ProducerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerThread,self).__init__()
        self.target = target
        self.name = name
        self.iniciar = True

    def run(self):
        finished = False
        while not finished:
            command = input(">>> ")
            globals()['attended_task'] = False

            if command == "list songs":
                getFilesList()
                globals()['attended_task'] = True

            #creates a new empty playlist
            elif command == "save playlist":
                if len(playlist_list) > 0:
                    globals()['playlist_index'] += 1
                globals()['playlist_list'].append(queue.Queue())
                globals()['data_playlist_list'].append([])
                for title in q.queue:
                    globals()['playlist_list'][playlist_index].put(title)
                for data in q_data:
                    globals()['data_playlist_list'][playlist_index].append(data)
                
                globals()['q'] = queue.Queue()
                globals()['q_data'] = []
                globals()['attended_task'] = True
            
            #stands on the selected playlist using a number
            elif command[0:4] == "use ":
                globals()['selected'] = int(command[-1])
                globals()['q'] = queue.Queue()
                globals()['q_data'] = []

                for title in playlist_list[selected].queue:
                    q.put(title)
                for data in data_playlist_list[selected]:
                    globals()['q_data'].append(data)

                globals()['attended_task'] = True

            elif command[0:8] == "enqueue ":
                song = command[8:]
                q.put(song)
                globals()['command'] = "enqueue"

            #gets the bytes of the song
            #from its name and removes it from the list of names and bytes
            elif command[0:8] == "dequeue ":
                song = command[8:]
                globals()['q_data'].pop(q.queue.index(song))
                q.queue.remove(song)
                globals()['attended_task'] = True

            elif command == "pause":
                globals()['command'] = "pause"

            elif command == "resume":
                globals()['command'] = "resume"

            #starts playing the playlist
            elif command == "next":
                globals()['command'] = "next"
            
            #starts playing the playlist
            elif command == "play":
                mixer.music.stop()
                globals()['command'] = "play"

            #stops playback
            elif command == "stop":
                globals()['command'] = "stop"
            
            elif command == "exit":
                finished = True
                globals()['command'] = "exit"

            
            elif command == "vars":
                print(globals()['command'], attended_task)
                globals()['attended_task'] = True
                
            #shows the playlist saved on the client
            elif command == "show playlist":
                for song in q.queue:
                    print('- ' + song)
                globals()['attended_task'] = True

            else:
                print("Invalid command")

        return

class ConsumerThread(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerThread,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        finished = False
        while not finished:
            for e in event.get():
                if e.type == MUSIC_END and len(q_data) > 0:
                    mixer.music.load(q_data[0])
                    globals()['q_data'].pop(0)
                    q.get()
                    mixer.music.play()

            if not attended_task:
                if command == "enqueue":
                    globals()['q_data'].append(io.BytesIO(loadSongBytes(q.queue[-1])))
                    globals()['command'] = ""
                    globals()['attended_task'] = True
                
                if command == "play":
                    globals()['command'] = ""
                    globals()['attended_task'] = True
                    play()
                
                if command == "pause":
                    mixer.music.pause()
                    globals()['command'] = ""
                    globals()['attended_task'] = True
                
                if command == "resume":
                    mixer.music.unpause()
                    globals()['command'] = ""
                    globals()['attended_task'] = True

                if command == "next":
                    globals()['command'] = ""
                    globals()['attended_task'] = True
                    play()
                
                if command == "exit":
                    mixer.music.stop()
                    finished = True
                    globals()['command'] = ""
                    globals()['attended_task'] = True

                if command == "stop":
                    mixer.music.stop()
                    globals()['command'] = ""
                    globals()['attended_task'] = True

                
                
        return

if __name__ == '__main__':
    p = ProducerThread(name='producer')
    c = ConsumerThread(name='consumer')

    p.start()
    time.sleep(2)
    c.start()
    time.sleep(2)