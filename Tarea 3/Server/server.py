import zmq
import os, sys

socket = zmq.Context().socket(zmq.REP)
socket.bind('tcp://*:5555')

#Creates the Files folder. If it already exists, pass
try:
    os.mkdir('Files')
except:
    pass

#Encodes a song file and returns its bytes
#If the is an error during the process, return Error message
def encodeFile(file):
    try:
        base64_image_b = open(file, 'rb').read()
        return base64_image_b
    except:
        return 'Error'

def getSongSize(song_path):
    return os.stat(song_path).st_size

def getChunkBytes(song_path, pointer):
    try:
        song = open(song_path, 'rb')
        song.seek(pointer, 0)
        chunk = song.read(500000)
        song.close()
        return chunk
    except:
        return b'Error'

#-------------------------------------------------------------------------
while True:
    msg = socket.recv_multipart()
    order = msg[0].decode('utf-8')
    print(order)

    if order == 'Download':
        file_name = "Files/" + msg[1].decode('utf-8') + ".mp3"
        encode_file_var = encodeFile(file_name)
        if encode_file_var == 'Error':
            msg = [b'Error']
        else:
            msg = [b'Ok', encode_file_var]
        socket.send_multipart(msg)

    elif order == 'Size':
        song_path = "Files/" + msg[1].decode('utf-8') + ".mp3"
        msg = [b'Ok', getSongSize(song_path).to_bytes(4, 'big')]
        socket.send_multipart(msg)
    
    elif order == 'Get Chunk':
        pointer = int.from_bytes(msg[2], 'big')
        song_path = "Files/" + msg[1].decode('utf-8') + ".mp3"
        msg = [b'Ok', getChunkBytes(song_path, pointer)]
        socket.send_multipart(msg)

    elif order == 'Listdir':
        dirs = os.listdir('Files/')
        msg = [b'Ok']
        for dir in dirs:
            dir = dir.replace('.mp3', '')
            msg.append(dir.encode('utf-8'))
        socket.send_multipart(msg)