# Example usage:
#
# python select_client.py alice localhost 3490
# python select_client.py bob localhost 3490
# python select_client.py chris localhost 3490
#
# The first argument is a prefix that the server will print to make it
# easier to tell the different clients apart. You can put anything
# there.
import json
import sys
import socket
import threading

from chatui import init_windows, read_command, print_message, end_windows


def usage():
    print("usage: select_client.py prefix host port", file=sys.stderr)


def main(argv):
    try:
        prefix = argv[1]
        host = argv[2]
        port = int(argv[3])
    except:
        usage()
        return 1

    # Make the client socket and connect
    s = socket.socket()
    s.connect((host, port))
    s.send(create_json_hello_packet(prefix).encode())

    init_windows()

    # We want 2 threads, one for reading from the server and one for reading from the user
    threads = [threading.Thread(target=handle_server_messages, args=(s,), daemon=True),
               threading.Thread(target=handle_user_messages, args=(s, prefix))]

    for thread in threads:
        thread.start()

    # Just wait until the read_command thread returns
    threads[1].join()
    end_windows()

    # now exit the program and kill the other thread
    return 0


def handle_user_messages(s, prefix):
    while True:
        message = read_command(prefix + "> ")
        if len(message) == 0:
            continue
        elif message[0] == "/":
            if message == "/q":
                s.close()
                return
            else:
                print_message("Unknown command")
        else:
            s.send(create_json_chat_packet(message).encode())


def handle_server_messages(s):
    while True:
        message = s.recv(4096).decode()
        message = json.loads(message)
        print_message(create_message_from_packet(message))


def create_message_from_packet(packet):
    if packet["type"] == "chat":
        return packet["nick"] + ": " + packet["message"]
    elif packet["type"] == "join":
        return "*** " + packet["nick"] + " has joined the chat"
    elif packet["type"] == "leave":
        return "*** " + packet["nick"] + " has left the chat"


def create_json_hello_packet(prefix):
    return json.dumps({"nick": prefix, "type": "hello"})


def create_json_chat_packet(message):
    return json.dumps({"message": message, "type": "chat"})


if __name__ == "__main__":
    sys.exit(main(sys.argv))
