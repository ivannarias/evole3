# irc_client.py
import socket
import threading
import argparse

# Font Formatting
bold = "\033[1m"
bold_red = "\033[1;31m"
bold_blue = "\033[1;34m"
bold_purple = "\033[1;35m"
reset_font = "\033[0m"
start_line = "\033[F\033[K"

def receive_messages(sock):
    while True:
        try:
	    data = sock.recv(1024)  # TODO HECHO: Receive data from socket
	    if not data:
               break
            pretty_print(data.decode())
        except:
            break

def pretty_print(message):
    if "PRIVMSG" in message:
        # TODO HECHO: Process PRIVMSG message
	prefix, _, resta = message.partition(" PRIVMSG ")
        sender = prefix[1:]  # Només eliminem els  ":"
        msg = resta.split(" :", 1)[1] if " :" in resta else ""
        print(f"{bold}({sender}): {reset_font}{msg}")

    elif "PART" in message:
        # TODO HECHO: Process PART mesage
        prefix, _, resta = message.partition(" PART ")
        sender = prefix[1:]
        channel = resta.strip()
        print(f"{bold_red}{sender} left the channel ({channel}){reset_font}")

    elif "JOIN" in message:
        # TODO HECHO: Process JOIN mesage
        prefix, _, resta = message.partition(" JOIN ")
        sender = prefix[1:]
        channel = resta.strip()
        print(f"{bold_red}{sender} joined the channel ({channel}){reset_font}")
    else:
        print (f"{bold}{message}{reset_font}")

def parse_command(cmd):
    if cmd.startswith("/nick "):
        return f"NICK {cmd[6:]}"
    elif cmd.startswith("/join"):
        return "JOIN #main"
    elif cmd.startswith("/part"):
        return "PART"
    elif cmd.startswith("/quit"):
        return "QUIT"
    else:
        # Treat as a channel message to #main if no command is detected
        return f"PRIVMSG #main :{cmd}"

def main():
    parser = argparse.ArgumentParser(description="IRC Client")
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Server IP address (default: 127.0.0.1)"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=6667,
        help="Server port (default: 6667)"
    )
    args = parser.parse_args()
    host = args.host
    port = args.port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # TODO HECHO: Add socket call
        s.connect((host,port))
        threading.Thread(target=receive_messages, args=(s,), daemon=True).start()
        try:
            while True:
                user_input = input()
                command = parse_command(user_input)
                if command:
                    # TODO HECHO: Add socket call
                    s.sendall((command + "\r\n").encode())
                    if command.startswith("QUIT"):
                        break
                    if command.startswith("PRIVMSG"):
                       print(f"{start_line}{bold_blue}(You):{reset_font} {user_input}")
                else:
                    print("Invalid command.")
        except KeyboardInterrupt:
            s.sendall(b"QUIT\r\n")

if __name__ == "__main__":
    main()
