import socket, threading, curses, re

HOST = "127.0.0.1"
PORT = 6667

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

messages = []

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

def strip_ansi(s):
    return ansi_escape.sub('', s)

def recv_loop(lock):
    while True:
        try:
            data = s.recv(4096).decode()
            if not data:
                with lock: messages.append("** disconnected **")
                break
            with lock:
                for line in data.strip().split("\n"):
                    messages.append(line)
        except:
            break

def main(stdscr):
    curses.curs_set(1)
    stdscr.clear()
    stdscr.nodelay(False)

    max_y, max_x = stdscr.getmaxyx()

    info_win = curses.newwin(1, max_x, 0, 0)
    chat_win = curses.newwin(max_y-2, max_x, 1, 0)
    input_win = curses.newwin(1, max_x, max_y-1, 0)

    lock = threading.Lock()
    threading.Thread(target=recv_loop, args=(lock,), daemon=True).start()

    buffer = ""
    while True:
        info_win.clear()
        info_win.addstr(0, 0, f"connected to EMX @ {HOST}:{PORT} | /quit to quit")
        info_win.refresh()

        chat_win.clear()
        with lock:
            for i, msg in enumerate(messages[-(max_y-3):]):
                clean = strip_ansi(msg)
                chat_win.addstr(i, 0, clean[:max_x-1])
        chat_win.refresh()

        input_win.clear()
        input_win.addstr(0, 0, "> " + buffer)
        input_win.refresh()

        ch = stdscr.getch()
        if ch in (curses.KEY_ENTER, 10, 13):
            if buffer.strip() == "/quit":
                break
            s.send(buffer.encode())
            buffer = ""
        elif ch in (curses.KEY_BACKSPACE, 127, 8):
            buffer = buffer[:-1]
        elif ch >= 32 and ch < 127:
            buffer += chr(ch)

    s.close()

if __name__ == "__main__":
    curses.wrapper(main)
