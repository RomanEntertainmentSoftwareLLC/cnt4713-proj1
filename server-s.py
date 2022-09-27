#!/usr/bin/env python3

# Jacob Roman
# 6343800
# 9/24/2022
# CNT4713
# Project 1: "Accio" File using TCP (Server Simplified)
# Purpose: Demonstrates useful functions on the server end of the software.

import sys
import socket
import signal
import time
import _thread
import errno

timeout = 10
max_clients = 10
not_stopped = False
client_num = 0
client = [0] * max_clients
address = [0] * max_clients
s = socket.socket()


def read_chunks(file_object, size):
    while True:
        if file_object:
            data = file_object.read(size)
            if not data:
                break
            yield data


def download_file(sock: socket, file_name: str, chunk_size: int):
    if file_name:
        data = b''
        downloaded = 0
        print("Receiving File...")

        wfile = open(file_name, 'wb')

        while True:
            try:
                wfile.write(data)
                data = sock.recv(chunk_size)
                print(data)
                if len(data) < 1024:
                    break
            except socket.timeout as e:
                sys.stderr.write("ERROR: Timeout on receiving data!\n".format(e))
                sock.close()
                sys.exit(2)
            except socket.error as e:
                sys.stderr.write("ERROR: Failed to receive data!\n".format(e))
                sock.close()
                sys.exit(2)
        wfile.close()
        print("Successfully downloaded the file!")
        return True

    else:
        return False


def connect_client():
    print("ACCEPT")
    global client_num
    global client
    global s
    global timeout

    while True:
        try:
            client_num += 1
            if client_num >= max_clients:
                client_num = max_clients
            s.settimeout(None)
            client[client_num], address[client_num] = s.accept()
        except socket.timeout as e:
            sys.stderr.write("ERROR: Timed out on accepting client " + str(client_num) + "\n".format(e))
            continue
        except socket.error as e:
            sys.stderr.write("ERROR: Failed on accepting client " + str(client_num) + "\n".format(e))
            continue
        s.settimeout(timeout)
        print("Connection from client " + str(client_num) + " has been established at " + str(address[client_num]))
        if client[client_num]:
            try:
                client[client_num].send(b'accio\r\n')
            except socket.timeout as e:
                sys.stderr.write("ERROR: Timeout on sending first data!\n".format(e))
            except socket.error as e:
                sys.stderr.write("ERROR: Failed to send the first data to client! \n".format(e))

            try:
                data = client[client_num].recv(2048)
            except socket.timeout as e:
                sys.stderr.write("ERROR: Timeout on receiving first data!\n".format(e))
            except socket.error as e:
                sys.stderr.write("ERROR: Failed to receive the first data from client! \n".format(e))
            print(data)

            try:
                client[client_num].send(b'accio\r\n')
            except socket.timeout as e:
                sys.stderr.write("ERROR: Timeout on sending second data!\n".format(e))
            except socket.error as e:
                sys.stderr.write("ERROR: Failed to send the second data to client! \n".format(e))

            try:
                data = client[client_num].recv(2048)
            except socket.timeout as e:
                sys.stderr.write("ERROR: Timeout on receiving second data!\n".format(e))
            except socket.error as e:
                sys.stderr.write("ERROR: Failed to receive the second data from client! \n".format(e))
            print(data)

            download_file(s, 'test', 1024)


def lost_client():
    global client_num
    global client

    while True:
        signal.signal(signal.SIGINT, handler)

        for i in range(max_clients):
            if remote_connection_closed(client[i]):
                print("Lost connection with client " + str(i))
                client_num -= 1
                if client_num <= 0:
                    client_num = 0
                client[i] = None


def remote_connection_closed(sock: socket) -> bool:
    if sock:
        try:
            buf = sock.recv(1, socket.MSG_PEEK | socket.MSG_DONTWAIT)
            if buf == b'':
                return True
        except BlockingIOError as exc:
            if exc.errno != errno.EAGAIN:
                raise
    return False


def handler(signum, frame):
    global not_stopped
    global s
    global client
    global address

    not_stopped = True

    while not_stopped:
        time.sleep(1)
        if signum == signal.SIGINT or signum == signal.SIGTERM or signum == signal.SIGQUIT:
            not_stopped = False
            s.close()
    print("Exit with code 0")
    exit(0)


def main(argv):
    host = "0.0.0.0"

    global s

    port = 0
    port_ok = False

    try:
        if len(str(argv)) >= 1:
            port = int(argv[0])
            port_ok = True
    except ValueError:
        sys.stderr.write("ERROR: Invalid port!")
        sys.exit(2)

    if port_ok:
        if port < 1 or port > 65535:
            sys.stderr.write("ERROR: Port number is out of range!\n")
            sys.exit(2)
    else:
        sys.stderr.write("ERROR: Port number is required!\n")
        exit(2)

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)
    except socket.error as e:
        sys.stderr.write("ERROR: Failed to create a socket! \n".format(e))
        s.close()
        sys.exit(2)

    try:
        s.bind((host, port))
    except socket.error as e:
        sys.stderr.write("ERROR: Failed to bind socket! \n".format(e))
        s.close()
        sys.exit(2)

    s.settimeout(timeout)
    s.listen(max_clients)

    _thread.start_new_thread(connect_client(), ())
    _thread.start_new_thread(lost_client(), ())


if __name__ == '__main__':
    main(sys.argv[1:])
