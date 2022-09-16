#!/usr/bin/env python3

# Jacob Roman
# 6343800
# 9/14/2022
# CNT4713
# Project 1: "Accio" File using TCP (Client)
# Purpose: Demonstrates useful functions on the client end of the software and tests them on a server.

import sys
import socket
import os
import time


def read_chunks(file_object, size):
    while True:
        data = file_object.read(size)
        if not data:
            break
        yield data


def send_data(s: socket, buffer):
    try:
        s.send(buffer)
    except socket.timeout as e:
        sys.stderr.write("ERROR: Timeout on sending data!\n".format(e))
        s.close()
        sys.exit(2)
    except socket.error as e:
        sys.stderr.write("ERROR: Failed to send data!\n".format(e))
        s.close()
        sys.exit(2)


def receive_data(s: socket):
    buffer = b''
    while True:
        try:
            data = s.recv(1)
            if len(data) == 0:
                sys.stderr.write("ERROR: Data is null\n")
                s.close()
                sys.exit(2)
        except socket.timeout as e:
            sys.stderr.write("ERROR: Timeout on receiving data!\n".format(e))
            s.close()
            sys.exit(2)
        except socket.error as e:
            sys.stderr.write("ERROR: Failed to receive data!\n".format(e))
            s.close()
            sys.exit(2)
        if data == b'\n':
            buffer += data
            break
        buffer += data
    return buffer


def emulate_timeout():
    print("Sending File")
    time.sleep(10)
    try:
        raise socket.timeout
    except socket.timeout as e:
        sys.stderr.write("ERROR: The server timed out its response".format(e))
    print("Successfully emulated a timeout error")


def upload_file(s: socket, file_name: str, file_mode: str, chunk_size: int):
    if file_name:
        if os.path.exists(file_name):
            percent = 0
            old_percent = 0
            uploaded = 0
            print("Sending File")
            file = open(file_name, file_mode)
            file_size = os.path.getsize(file_name)
            for file_buf in read_chunks(file, chunk_size):
                while file_buf:
                    try:
                        s.send(file_buf)
                    except socket.timeout as e:
                        sys.stderr.write("ERROR: Timeout on sending data!\n".format(e))
                        s.close()
                        sys.exit(2)
                    except socket.error as e:
                        sys.stderr.write("ERROR: Failed to send data!\n".format(e))
                        s.close()
                        sys.exit(2)
                    uploaded += chunk_size
                    percent = int((uploaded / file_size) * 100)
                    if percent != old_percent and percent != 100:
                        print("Uploaded: " + str(int(percent)) + "%")
                        old_percent = percent
                    if percent >= 100:
                        percent = 100
                        old_percent = 100
                        break
                if percent >= 100:
                    print("Uploaded: " + str(percent) + "%")
                    break

            file.close()
            return True
        else:
            print("ERROR: File not found")
            s.close()
            sys.exit(2)
    else:
        return False


def main(argv):
    host = ""
    s = socket.socket()

    if len(argv) >= 1:
        host = str(argv[0])
    elif len(argv) == 0:
        print("ERROR: Host and port are required!\n")
        exit(2)

    port = 0
    port_ok = False

    try:
        if len(argv) >= 2:
            port = int(argv[1])
            port_ok = True
    except ValueError:
        sys.stderr.write("ERROR: invalid port!")
        sys.exit(2)

    if port_ok:
        if port < 1 or port > 65535:
            print("ERROR: port number is out of range!\n")
            sys.exit(2)
    else:
        print("ERROR: Host and port are required!\n")
        exit(2)

    filename = ''

    if len(argv) >= 3:
        filename = str(argv[2])

    print(host + ", " + str(port) + ", " + filename)

    try:
        host_ip = socket.gethostbyname(host)
    except socket.error as e:
        sys.stderr.write("ERROR: Failed to resolve host\n".format(e))
        sys.exit(2)

    print(host_ip)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
    except socket.error as e:
        sys.stderr.write("ERROR: Failed to create a socket! \n".format(e))
        s.close()
        sys.exit(2)

    s.settimeout(10)

    try:
        s.connect((host, port))
    except socket.error as e:
        sys.stderr.write("ERROR: Failed to connect to host!\n".format(e))
        s.close()
        sys.exit(2)

    print("Successfully connected to " + str(host) + " at port " + str(port) + '\n')

    print('First attempt on receiving data')
    buffer = b"confirm-" + receive_data(s)

    print('Send first received buffer data back to the server')
    send_data(s, buffer)

    print('Second attempt on receiving data')
    buffer = b''
    temp_str = receive_data(s)
    str_size = len(temp_str)
    again = b'-again'
    special_chars = temp_str[str_size - 2:]
    temp = bytearray(b'confirm-')
    temp[8:8] = bytearray(temp_str)
    temp[13:13] = bytearray(again)
    temp[22:22] = bytearray(special_chars)
    lst = list()

    for i in range(len(temp)):
        lst.append(chr(temp[i]))
        buffer += lst[i].encode()

    print('Send second received buffer data back to the server')
    send_data(s, buffer)
    emulate_timeout()
    upload_file(s, filename, 'rb', 10000)
    print("Success! Closing socket.")
    s.close()


if __name__ == '__main__':
    main(sys.argv[1:])
