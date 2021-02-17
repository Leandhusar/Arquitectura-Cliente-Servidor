import base64
import zmq
import os, sys

socket = zmq.Context().socket(zmq.REP)
socket.bind('tcp://*:5555')

try:
    os.mkdir('Files')
except:
    pass

def encodeFile(file):
    try:
        base64_image_b = open(file, 'rb').read()
        return base64_image_b
    except:
        return False

def saveFile(file, new_file_name):
    try:
        with open(new_file_name, 'wb') as new_file:
            new_file.write(file)
    except:
        pass

while True:
    msg = socket.recv_multipart()
    order = msg[0].decode('utf-8')
    print(order)

    if order == 'Download':
        file_name = "Files/" + msg[1].decode('utf-8')
        encode_file_var = encodeFile(file_name)
        if encode_file_var == False:
            msg = [b'Empty']
        else:
            msg = [b'Ok', encode_file_var]
        socket.send_multipart(msg)
    elif order == 'Upload':
        file_data = msg[1]
        file_to_save_name = msg[2].decode('utf-8')
        saveFile(file_data, "Files/" + file_to_save_name)
        msg = [b'Ok']
        socket.send_multipart(msg)
    elif order == 'Listdir':
        dirs = os.listdir('Files/')
        msg = [b'Ok']
        for dir in dirs:
            msg.append(dir.encode('utf-8'))
        socket.send_multipart(msg)