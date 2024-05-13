import socket
import threading
import json
import time
from colorama import Fore
import os


_version_ = "1.1.1"

HOST = "0.0.0.0"
PORT = 7777


tries = {}      # login tries
conns = []      # -> conn <- , addr = s.accept()

usersLogged = {}    # {username: conn}



def CheckFiles():
    files = ['accs.json', 'banned.json', 'bannedAccs.json']

    for i in files:
        open(i, "w").write("{}") if os.path.isfile(i) == False else None



def recvMessage(conn: socket.socket, addr, username):

    ex = False

    conn.settimeout(60*3)   # After 3 minutes you get disconnected for inactivity

    while ex == False:
        try:
            message = conn.recv(1024).decode('utf-32-be')

            if message == "\\exit":                         # If the message is \exit, the server close the connection with the client
                conn.close()
                conns.remove(conn)                          # Remove the connection from the list of all the connections
                usersLogged.pop(username)                   # Remove the user on the userLogged list

                message = Fore.RED + "\n[SERVER]: " + username + " QUITTED\n" + Fore.RESET

                print(message)

                tmp = None

                # Send to evryone that the user quitted

                try:
                    for x in conns:
                        if x is not conn:
                            tmp = x
                            x.send(message.encode('utf-32-be'))

                except:
                    conns.remove(tmp)

                break

            elif message == "\\list":                       # If the message is \list, the server send to the client the list of the logged users

                message = "\n" + Fore.GREEN

                for i in usersLogged:
                    message += "\t[" + i + "]\n"

                message += Fore.RESET

                conn.send(message.encode('utf-32-be'))

            # --------------------------- DM ---------------------------


            elif message.split(" ")[0] == "\\dm" and len(message.split(" ")) >= 3 and message.split(" ")[1] in usersLogged:
                print(addr[0] + ":(" + "[" + username + "] -> " + message.split(" ")[1] + ") ==> " + message + "\n")
                
                user = message.split(" ")[1]

                message = "[" + username + "] ==> " + message.replace((message.split(" ")[0] + " " + message.split(" ")[1]) + " ", "") + "\n"

                if username == "admin":
                    message = Fore.YELLOW + message + Fore.RESET

                usersLogged[user].send(message.encode('utf-32-be'))
            

            elif message.split(" ")[0] == "\\dm" and len(message.split(" ")) < 3:
                message = Fore.YELLOW + "[SERVER] dm syntax: \\dm <username> <message>" + Fore.RESET

                conn.send(message.encode('utf-32-be'))
            
            elif message.split(" ")[0] == "\\dm" and len(message.split(" ")) >= 3 and message.split(" ")[1] not in usersLogged:
                message = Fore.RED + "[SERVER] Username not found!" + Fore.RESET

                conn.send(message.encode('utf-32-be'))


            #END DM


            # --------------------------- BAN ---------------------------

            elif message.split(" ")[0] == "\\ban" and username == "admin" and len(message.split(" ")) == 3 and message.split(" ")[1] in json.load(open("accs.json", "rt")) and message.split(" ")[1] not in json.load(open("bannedAccs.json", "rt")):
                bannedUser = json.load(open("bannedAccs.json", "rt"))
                bannedUser.update({message.split(" ")[1]: (time.time() + int(message.split(" ")[2]))})
                json.dump(bannedUser, open("bannedAccs.json", "wt"))

                if message.split(" ")[1] in usersLogged:
                    usersLogged[message.split(" ")[1]].send('501'.encode('utf-32-be'))
                    usersLogged[message.split(" ")[1]].close()
                    usersLogged.pop(message.split(" ")[1])

                message = Fore.YELLOW + "\n[SERVER] " + message.split(" ")[1] + " banned successfully!\n" + Fore.RESET
                print(message)

                for x in conns:
                    x.send(message.encode('utf-32-be'))
            

            elif message.split(" ")[0] == "\\ban" and username != "admin":
                message = Fore.RED + "[SERVER] You don't have the permissions to execute the ban" + Fore.RESET
                conn.send(message.encode('utf-32-be'))

            elif message.split(" ")[0] == "\\ban" and len(message.split(" ")) != 3 and username == "admin":
                message = Fore.YELLOW + "[SERVER] ban syntax: \\ban <username> <seconds>" + Fore.RESET
                conn.send(message.encode('utf-32-be'))

            elif message.split(" ")[0] == "\\ban" and message.split(" ")[1] in json.load(open("bannedAccs.json", "rt")):
                message = Fore.YELLOW + "[SERVER] User already banned" + Fore.RESET
                conn.send(message.encode('utf-32-be'))


            # END BAN

            # --------------------------- UNBAN ---------------------------

            elif message.split(" ")[0] == "\\unban" and username == "admin" and len(message.split(" ")) == 2 and message.split(" ")[1] in json.load(open("bannedAccs.json", "rt")):
                bannedUser = json.load(open("bannedAccs.json", "rt"))
                bannedUser.pop(message.split(" ")[1])
                json.dump(bannedUser, open("bannedAccs.json", "wt"))

                message = Fore.GREEN + "\n[SERVER] " + message.split(" ")[1] + " unbanned successfully!\n" + Fore.RESET
                print(message)
                conn.send(message.encode('utf-32-be'))


            elif message.split(" ")[0] == "\\unban" and len(message.split(" ")) != 2 and username == "admin":
                message = Fore.YELLOW + "[SERVER] unban syntax: \\ban <username>" + Fore.RESET
                conn.send(message.encode('utf-32-be'))

            elif message.split(" ")[0] == "\\unban" and message.split(" ")[1] not in json.load(open("bannedAccs.json", "rt")) and username == "admin":
                message = Fore.YELLOW + "[SERVER] User not banned" + Fore.RESET
                conn.send(message.encode('utf-32-be'))

            elif message.split(" ")[0] == "\\unban" and username != "admin":
                message = Fore.RED + "[SERVER] You don't have the permissions to execute the ban" + Fore.RESET
                conn.send(message.encode('utf-32-be'))


            # END UNBAN


            # --------------------------- KICK USER ---------------------------


            elif message.split(" ")[0] == "\\kick" and len(message.split(" ")) == 2 and username == "admin" and message.split(" ")[1] in usersLogged:
                usersLogged[message.split(" ")[1]].send('507'.encode('utf-32-be'))
                usersLogged[message.split(" ")[1]].close()
                usersLogged.pop(message.split(" ")[1])
                message = Fore.GREEN + "\n[SERVER] " + username + " kicked!" + Fore.RESET


            elif message.split(" ")[0] == "\\kick" and len(message.split(" ")) != 2 and username == "admin":
                message = Fore.YELLOW + "[SERVER] kick syntax: \\kick <username>" + Fore.RESET
                conn.send(message.encode('utf-32-be'))

            elif message.split(" ")[0] == "\\kick" and username != "admin":
                message = Fore.RED + "[SERVER] You don't have the permissions to execute the ban" + Fore.RESET
                conn.send(message.encode('utf-32-be'))


            # END KICK USER

            # --------------------------- SEND NORMAL MESSAGE ---------------------------


            elif message != '':
                message = "[" + username + "] ==> " + message + "\n"

                if username == "admin":
                    message = Fore.YELLOW + message + Fore.RESET

                print(addr[0] + ":" + message)

                tmp = None

                try:
                    for x in conns:
                        if x is not conn:
                            tmp = x
                            x.send(message.encode('utf-32-be'))

                except:
                    pass

        except TimeoutError:

            message = Fore.RED + "\n[SERVER]: Disconnected " + username + " for inactivity"

            print(message)

            for x in conns:
                if x is not conn:
                    tmp = x
                    x.send(message.encode('utf-32-be'))

            conns.remove(tmp)

            conn.send("550".encode('utf-32-be'))

            conns.remove(conn)
            usersLogged.pop(username)
            conn.close()
            ex = True
        
        except OSError:
            pass



def auth(conn: socket.socket, addr):
    accounts = json.load(open("accs.json", "rt"))           # Get the list of the users
    bannedIp = json.load(open("banned.json", "rt"))         # Get the lidt of the banned ip
    bannedUsers = json.load(open("bannedAccs.json", "rt"))  # Get the list of the banned users

    global conns

    if addr[0] in bannedIp:
        if bannedIp[addr[0]] - time.time() > 0:

            conn.send("500".encode('utf-32-be'))            # If the ip is banned, send the code 500 and close the connection
            conn.close()
        else:
            bannedIp.pop(addr[0])                           # If the ip is banned but the time is expired, remove the ip to the banned list
            json.dump(bannedIp, open("banned.json", "wt"))  # Update the ip-banned list

    else:
        conn.send('404'.encode('utf-32-be'))                # Sent the code 404 to start the authentication

        checkVersion = conn.recv(1024).decode('utf-32-be')  # Check the client version if chech with the server version

        if checkVersion != _version_:
            conn.send('Err'.encode('utf-32-be'))            # If the versions doesn't match, the server send to the client the payload 'Err' and close the connection
            conn.close()

        else:

            conn.send('OK'.encode('utf-32-be'))             # If the versions match, the server send the payload 'OK'

            username = conn.recv(1024).decode('utf-32-be')  # Get the username

            if username in accounts and username not in usersLogged and username not in bannedUsers:

                conn.send("200".encode('utf-32-be'))        # If the user exist and is not in the banned users and is not already logged, send the code 200 (username valid)

                tries.update({username: 0})                 # Init the tries number of the user

                logged = False

                while tries[username] != 5 and logged == False:

                    password = conn.recv(1024).decode('utf-32-be')

                    if accounts[username] == password:
                        conn.send("200".encode('utf-32-be'))
                        logged = True
                        conns.append(conn)                      # Append the connection on the list of all the connections
                        usersLogged.update({username: conn})    # Append the user with is connection

                        print(Fore.GREEN + "\n[SERVER]: " + username + " LOGGED\n" + Fore.RESET)

                        tmp = None

                        # Send to evryone connected that the user is connected

                        try:
                            for x in conns:
                                if x is not conn:
                                    tmp = x
                                    message = Fore.GREEN + "\n[SERVER]: " + username + " LOGGED\n" + Fore.RESET
                                    x.send(message.encode('utf-32-be'))


                        except:
                            conns.remove(tmp)

                        recvMessage(conn, addr, username)                # Start a new session with the user

                    elif tries[username] < 5 and logged == False:
                        conn.send("404".encode('utf-32-be'))                # If the password is wrong, send the 404 code
                        tries.update({username: (tries[username] + 1)})     # Update the tries number

                if tries[username] == 5:
                    conn.send("500".encode('utf-32-be'))                    # Send the code, saying at the client that the ip is banned
                    bannedIp.update({addr[0]: time.time() + (60*5)})        # Add the ip to the ip-banned list with the time of the ban (5 minutes)

                    json.dump(bannedIp, open("banned.json", "wt"))          # Update the list of the banned ip

                else:
                    tries.update({username: 0})


            elif username in usersLogged:                       # Else if the user is already logged, the server send the code 502
                conn.send('502'.encode('utf-32-be'))
                conn.close()

            elif username in bannedUsers:
                if bannedUsers[username] - time.time() > 0:     # Else if the user is in the banned users, send the code 501

                    conn.send("501".encode('utf-32-be'))
                    conn.close()
                
                else:                                           # Else if the user is in the banned users but the time is expired, remove the user in the banned accounts list and send the code 501
                    bannedUsers.pop(username)
                    json.dump(bannedUsers, open("bannedAccs.json", "wt"))
                    
                    conn.send("501".encode('utf-32-be'))
                    conn.close()

            else:
                conn.send("404".encode('utf-32-be'))            # Else send the code 404 and close the connection
                conn.close()



if __name__ ==  "__main__":
    CheckFiles()                                                    # Check fi all the json files exist
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           # Init the socket
    s.bind((HOST, PORT))

    print("Listening on " + HOST + ":" + str(PORT) + "\n\n")

    while True:
        s.listen()                                                  # Start listening
        conn, addr = s.accept()                                     # Accept the new connection
        t = threading.Thread(target=auth, args=(conn, addr,))     # Create a new thread
        t.start()                                                   # Start the new thread
