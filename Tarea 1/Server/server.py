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
        base64_image = base64.b64encode(open(file, 'rb').read())
        base64_image = base64_image.decode('utf-8')
        base64_image_b = base64_image.encode('utf-8')
        return base64_image_b
    except:
        return False

def saveFile(file, new_file_name):
    try:
        with open(new_file_name, 'wb') as new_file:
            decode_new_file = base64.decodebytes(file)
            new_file.write(decode_new_file)
    except:
        pass

while True:
    msg = socket.recv_multipart()
    print(msg)
    order = msg[0].decode('utf-8')

    if order == 'Download':
        file_name = "Files/" + msg[1].decode('utf-8')
        encode_file_var = encodeFile(file_name)
        if encode_file_var == False:
            msg = [b'Empty']
        else:
            msg = [b'Ok', encodeFile(file_name)]
        socket.send_multipart(msg)
    elif order == 'Upload':
        file_data = msg[1]
        file_to_save_name = msg[2].decode('utf-8')
        saveFile(file_data, "Files/" + file_to_save_name)
        msg = [b'Ok']
        socket.send_multipart(msg)
    elif order == 'Listdir':
        dirs = os.listdir('Files/')
        msg = []
        for dir in dirs:
            msg.append(dir.encode('utf-8'))
        socket.send_multipart(msg)