import base64
import zmq
import os, sys

socket = zmq.Context().socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

def encodeFile(file):
    base64_image = base64.b64encode(open(file, 'rb').read())
    base64_image = base64_image.decode('utf-8')
    base64_image_b = base64_image.encode('utf-8')
    return base64_image_b

def saveFile(file, new_file_name):
    with open(new_file_name, 'wb') as new_file:
        decode_new_file = base64.decodebytes(file)
        new_file.write(decode_new_file)

def downloadFile(file_name, local_file_name):
    msg = [b'Download', file_name.encode('utf-8')]
    socket.send_multipart(msg)
    msg = socket.recv_multipart()
    if len(msg) != 1:
        file_data = msg[1]
        saveFile(file_data, local_file_name)
    else:
        print('It was not possible to download this file', msg)

def uploadFile(file_name, name_to_save):
    msg = [b'Upload', encodeFile(file_name), name_to_save.encode('utf-8')]
    socket.send_multipart(msg)
    msg = socket.recv_multipart()

def getFilesList():
    msg = [b'Listdir']
    socket.send_multipart(msg)
    msg = socket.recv_multipart()
    print('Server directories:')
    for dir in msg:
        print("- " + dir.decode('utf-8'))

def main():
    if len(sys.argv) < 2:
        print('Operation (listdir, download, upload) is required')
    elif sys.argv[1] == 'download':
        if len(sys.argv) != 4:
            print('Download operation requires the file name from the server and the name the file is going to be called in local')
        else:
            server_file = sys.argv[2]
            local_name = sys.argv[3]
            try:
                downloadFile(server_file, local_name)
            except:
                print('It was not possible to download this file')
    elif sys.argv[1] == 'upload':
        if len(sys.argv) != 4:
            print('Upload operation requires the file name from PC and the name the file is going to be called in server')
        else:
            local_file_name = sys.argv[2]
            server_file_name = sys.argv[3]
            try:
                uploadFile(local_file_name, server_file_name)
            except:
                print('It was not possible to upload this file')
    elif sys.argv[1] == 'listdir':
        if len(sys.argv) == 2:
            try:
                getFilesList()
            except:
                print('It was not possible to see server files')
    else:
        print('That commando does not exist')

if __name__ == '__main__':
    main()