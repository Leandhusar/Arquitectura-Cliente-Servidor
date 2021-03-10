import threading
import time
import random
import queue
import zmq
import os, sys
from pygame import mixer
import io

#Setting socket and connection to server
socket = zmq.Context().socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

#Initialize music mixer
mixer.init()

command = ""
attended_task = True
q = queue.Queue()
q_data = []


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

def play(song_bytes):
    try:
        mixer.music.load(io.BytesIO(song_bytes))
        mixer.music.set_volume(0.5)
        mixer.music.play()
    except:
        pass

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
                mixer.music.pause()

            elif command == "resume":
                mixer.music.unpause()

            #starts playing the playlist
            elif command == "next":
                globals()['command'] = "next"
            
            #starts playing the playlist
            elif command == "play":
                globals()['command'] = "play"

            #stops playback
            elif command == "stop":
                mixer.music.stop()
            
            elif command == "exit":
                mixer.music.stop()
                finished = True
                sys.exit()
                
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
        while True:
            if not attended_task:
                if command == "enqueue":
                    globals()['q_data'].append(loadSongBytes(q.queue[-1]))
                    globals()['command'] = ""
                    globals()['attended_task'] = True
                
                if command == "play" or command == "next":
                    song_bytes = q_data[0]
                    globals()['q_data'].pop(0)
                    q.get()
                    play(song_bytes)
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