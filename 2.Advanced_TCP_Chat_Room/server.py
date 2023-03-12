import socket
import threading

host = '127.0.0.1'
port = 34562

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
usernames = []

def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if usernames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused!'.encode('ascii'))
            elif msg.decode('ascii').startswith('BAN'):
                if usernames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            else:
                broadcast(message)
        except:
            if client in clients:
                index = clients.index(client)
                clients.remove(client)
                client.close()
                username = usernames[index]
                broadcast(f'{username} left the chat!'.encode('ascii'))
                usernames.remove(username)
                break

def receive():
    global password
    while True:
        client, address = server.accept()
        print(f'Connected with {str(address)}')

        client.send('USER'.encode('ascii'))

        username = client.recv(1024).decode('ascii')

        with open('bans.txt', 'r') as f:
            bans = f.readlines()

        if username+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if username == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            if password != 'letmein':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        usernames.append(username)
        clients.append(client)

        print(f'Username of the client is {username}!')
        broadcast(f'{username} joined the chat!'.encode('ascii'))
        client.send('Connected to the Server!'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

def kick_user(name):
    if name in usernames:
        name_index = usernames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were removed by an admin!'.encode('ascii'))
        client_to_kick.close()
        usernames.remove(name)
        broadcast(f'{name} was removed by an admin!'.encode('ascii'))

print("Sever is listening..........")
receive()
