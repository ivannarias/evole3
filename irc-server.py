# irc_server.py
import socket
import threading

HOST = ''
PORT = 6667
CHANNEL = "main"

users = {}  # associate connections -> to nicknames
channel_members = set()

def broadcast(message, exclude=None):
    for client in channel_members:
        if client != exclude:
            try:
                client.sendall(message.encode())
            except:
                pass

def command_NICK(conn, message):
    parts = message.split()
    if len(parts) < 2 or not parts[1].strip():
        return ":server 431 * :No nickname given\r\n"

   proposed_nick = parts[1]  # Agafem el nickname proposat

    # TODO HECHO: Check if nick in use
    if proposed_nick in users.values():  # Comprovem que no hi hagi usuaris amb aquest nick
	return f":server 433 * {proposed_nick} :Nickname is already in use\r\n"

    # TODO HECHO: Check if nickname contains invalid characters
    if not proposed_nick.isalnum():  # Comprovem que no tingui caràcters invàlids
	return f":server 432 * {proposed_nick} :Erroneous nickname\r\n"

    #TODO HECHO; save nickname in corresponding array and send confirmation
    users[conn] = proposed_nick
    return f":server 001 {proposed_nick} :Welcome to the server\r\n"

def command_JOIN(conn, message):
    if conn not in users:
        return ":server 451 * :You have not registered\r\n"

    nickname = users[conn] #TODO HECHO Retrieve current user nickname
    parts = message.split() #  Separem el missatge

    #TODO HECHO: Wrong channel provided
    if len(parts) < 2 or not parts[1].startswith("#"):  # És invalid si no comença per "#" o si no té 1 o menys parts
	return f":server 403 {nickname} :No such channel\r\n"

    if conn not in channel_members:
        # TODO HECHO: Add user to channel
        # Notify all other users that someone joined
	channel_members.add(conn)  # Afegim el membre als membres del canal
        broadcast(f":{nickname} JOIN :#{CHANNEL}\r\n", exclude=conn)
    # Send confirmation to the user
    return f":server 332 {nickname} #{CHANNEL} :Welcome to #{CHANNEL}\r\n"

def command_PART(conn, message):
    if conn not in users:
        return ":server 451 * :You have not registered\r\n"

    nickname = users[conn]  #TODO HECHO: Retrieve current user nickname
    if conn in channel_members:
        # TODO HECHO remove user from channel
        # Notifiy all other users that this user left.
        channel_members.remove(conn)
	broadcast(f":{nickname} PART #{CHANNEL}\r\n", exclude=conn)
    # Confirm to current user that leaving was accepted
    return f":{nickname} PART #{CHANNEL}\r\n"

def command_QUIT(conn, message):

    nickname = nickname = users.get(conn, "*")  #TODO HECHO retrieve current nickname
    if conn in channel_members:
        #TODO HECHO: Remove user from channel
	channel_members.remove(conn)
        broadcast(f":{nickname} QUIT :Client disconnected\r\n", exclude=conn)
    #TODO HECHO: remove user from list of users.
    # Send confirmation to user
    if conn in users:
        del users[conn]

    return f":server ERROR :Closing Link: {nickname}\r\n"

def command_PRIVMSG(conn, message):
    if conn not in users:
        return ":server 451 * :You have not registered\r\n"

    parts = message.split(" ", 2)
    if len(parts) < 3 or not parts[2].startswith(":"):
        return ":server 412 * :No text to send\r\n"

    target = parts[1]  #TODO
    msg = parts[2][1:]  #TODO
    nickname = users[conn]

    if target == f"#{CHANNEL}":
        if conn not in channel_members:
            return f":server 442 {nickname} #{CHANNEL} :You're not on that channel\r\n"
        # TODO HECHO: Send MSG to everyone on the channel
        broadcast(f":{nickname} PRIVMSG #{CHANNEL} :{msg}\r\n", exclude=conn)
	return ""  # Message broadcasted no need to for single reply to client
    else:
        # Reject anything that's not the main channel
        return f":server 401 {nickname} {target} :No such nick/channel\r\n"

def handle_client(conn, addr):
    conn.sendall(b":server NOTICE * :Welcome! Please use /nick <name>\r\n")
    print (f"New client connects to server: {addr}")
    try:
        while True:
            data = conn.recv(1024) # TODO HECHO: Receive data from socket
            if not data:
                break

            message = data.decode().strip()
            command = message.split()[0].upper()
            handler = globals().get(f"command_{command}")
            if handler:
                response = handler(conn, message)
                if response:
                    conn.sendall(response.encode())
                if command == "QUIT":
                    break
            else:
                conn.sendall(b":server 421 * :Unknown command\r\n")
    finally:
        if conn in channel_members:
            channel_members.remove(conn)
        if conn in users:
            del users[conn]
        conn.close()
        print (f"Client leaves the server: {addr}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # TODO HECHO: Add required socket calls for server
	s.bind((HOST, PORT))  # Asociem el socket a la IP i el port
        s.listen()  # Posem el socket a escoltar al host / port on ens hem associat
        print(f"IRC Server listening on {HOST}:{PORT}")
        while True:
	    conn, addr = s.accept()  # Acceptem totes aquelles connexions
            # TODO HECHO: Add required socket calls for server
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    main()
