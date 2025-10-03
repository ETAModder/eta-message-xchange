import socket, select, datetime, sys

HOST = "0.0.0.0"
PORT = 6667
PASSWORD = None
MOTD = "welcome to EMX!"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(10)

sockets = [server]
clients = {}

COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RED = "\033[91m"
COLOR_BLUE = "\033[94m"
COLOR_MAGENTA = "\033[95m"

BANNER = f"""
{COLOR_MAGENTA}┌───────────────────────────────┐
│   ETA Message Xchange (EMX)   │
└───────────────────────────────┘{COLOR_RESET}
"""

def broadcast(sender, message, include_sender=False):
    for s in clients:
        if include_sender or s != sender:
            try:
                s.send(message.encode())
            except:
                s.close()
                if s in sockets: sockets.remove(s)
                if s in clients: del clients[s]

print(BANNER)
print(f"EMX server running on {HOST}:{PORT}")

while True:
    r, _, _ = select.select(sockets, [], [])
    for sock in r:
        if sock == server:
            conn, addr = server.accept()
            conn.send(b"enter username: ")
            username = conn.recv(1024).decode().strip()
            if PASSWORD:
                conn.send(b"enter password: ")
                pw = conn.recv(1024).decode().strip()
                if pw != PASSWORD:
                    conn.send(f"{COLOR_RED}wrong password{COLOR_RESET}\n".encode())
                    conn.close()
                    continue
            sockets.append(conn)
            clients[conn] = username
            print(f"{username} joined from {addr}")
            conn.send(f"{BANNER}\n{COLOR_BLUE}{MOTD}{COLOR_RESET}\n".encode())
            broadcast(conn, f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {COLOR_GREEN}* {username} joined{COLOR_RESET}\n", include_sender=True)
        else:
            try:
                data = sock.recv(4096).decode().strip()
                if data:
                    if data.startswith("/"):
                        cmd = data.split()[0].lower()
                        if cmd == "/who":
                            userlist = ", ".join(clients.values())
                            sock.send(f"{COLOR_YELLOW}Users online: {userlist}{COLOR_RESET}\n".encode())
                        elif cmd == "/motd":
                            sock.send(f"{COLOR_BLUE}{MOTD}{COLOR_RESET}\n".encode())
                        elif cmd == "/broadcast":
                            msg = " ".join(data.split()[1:])
                            broadcast(sock, f"{COLOR_MAGENTA}[BROADCAST] {msg}{COLOR_RESET}\n", include_sender=True)
                        else:
                            sock.send(f"{COLOR_RED}unknown cmd{COLOR_RESET}\n".encode())
                    else:
                        msg = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {COLOR_GREEN}{clients[sock]}{COLOR_RESET} > {data}\n"
                        sys.stdout.write(msg)
                        broadcast(sock, msg, include_sender=True)
                else:
                    if sock in clients:
                        left = clients[sock]
                        broadcast(sock, f"{COLOR_RED}* {left} left{COLOR_RESET}\n", include_sender=True)
                        del clients[sock]
                    sockets.remove(sock)
            except:
                continue
