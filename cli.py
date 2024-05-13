import socket
import threading
import sys
import getpass
import os
from hashlib import sha256



RED = "\x1b[31m"
RESET = "\x1b[39m"
GREEN = "\x1b[32m"

_version_ = "1.1.0"

HOST = "127.0.0.1"
PORT = 7777

ex = False



def clean():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def recvMessage(s: socket.socket):
    global ex

    while ex == False:
        message = s.recv(1024)

        if message == '550'.encode('utf-32-be'):
            print(RED + "\n\n[SERVER] Disconnected for inactivity!" + RESET + "\n\nPress Enter to continue")

            ex = True

        elif message == '501'.encode('utf-32-be'):
            print(RED + "\n\n[SERVER] Your account is banned" + RESET + "\n\nPress enter to continue")
            s.close()

            ex = True

        elif message == '507'.encode('utf-32-be'):
            print(RED + "\n\n[SERVER] you got kicked" + RESET + "\n\nPress enter to continue")
            s.close()

            ex = True

        elif message != ''.encode('utf-32-be'):
            print("\r", end="")
            print("\r\n" + message.decode('utf-32-be') + "\n -> ", end="")


def sendMessage(s: socket.socket):
    global ex

    while ex == False:

        try:
            message = input(" -> ")
        except:
            message = "\\exit"

            ex = True

        if message == "\\clear":
            clean()

        elif message == "\\version":
            print("\n" + GREEN + "[VERSION]: " + _version_ + RESET)

        else:
            if ex == False:
                s.send(message.encode('utf-32-be'))

            if message == "\\exit":
                ex = True



def auth(s: socket.socket):
    code = s.recv(1024)

    if code == '500'.encode('utf-32-be'):
        print("The ip is banned!")
        s.close()
        sys.exit()
        
    s.send(_version_.encode('utf-32-be'))

    checkVersion = s.recv(1024).decode('utf-32-be')

    if checkVersion == 'Err':
        print("\nError, cli and server have a different version")

        s.close()

    else:
        username = input("\n\nEnter the username: ")

        s.send(username.encode('utf-32-be'))

        resp = s.recv(1024)

        if resp == "200".encode('utf-32-be'):
            while code == '404'.encode('utf-32-be'):
                password = getpass.getpass("Enter the password: ")

                password = sha256(password.encode()).hexdigest()

                s.send(password.encode('utf-32-be'))

                code = s.recv(1024)

                if code == '404'.encode('utf-32-be'):
                    print("\nInvalid password!")

                elif code == '200'.encode('utf-32-be'):
                    clean()
                    print("\n-------------- WELCOME BACK " + username.upper() + " --------------\n\n")

        elif resp == '404'.encode('utf-32-be'):
            print("\nInvalid username")

        elif resp == '502'.encode('utf-32-be'):
            print("\nError, user already logged in")

        elif resp == '501'.encode('utf-32-be'):
            print("\nError, the user is banned")

        if code == "200".encode('utf-32-be'):
            threading.Thread(target=recvMessage, args=(s,)).start()
            threading.Thread(target=sendMessage, args=(s,)).start()


        elif code == "500".encode('utf-32-be'):
            print("Error, the ip is banned for 5 minute")


if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    auth(s)
