import json
import sys
import socket
import select


def run_server(port):
    # Make the server socket and bind it to the port
    client_name_map = {}
    server_socket = socket.socket()
    server_socket.bind(("", port))
    server_socket.listen()

    # The listener socket
    read_sockets = [server_socket]

    # Loop forever
    while True:
        # call select() and get the sockets that are ready to read
        ready_to_read, _, _ = select.select(read_sockets, [], [])

        # for each socket that is ready to read
        for s in ready_to_read:
            # if the socket is the listener socket, then accept the connection
            if s is server_socket:
                client_socket, _ = server_socket.accept()
                read_sockets.append(client_socket)


            # else it is a regular socket
            else:
                message = s.recv(4096)

                # If the message is empty, the client has disconnected
                if not message:
                    s.close()
                    read_sockets.remove(s)
                    client_name = client_name_map.pop(s)
                    broadcast_message(create_json_leave_packet(client_name), client_name_map)
                    print(f"*** {client_name} has left the chat")
                else:
                    handle_packet(s, message.decode(), client_name_map)


def handle_packet(s, message, client_name_map):
    packet = json.loads(message)

    if packet["type"] == "hello":
        print(f"*** {packet['nick']} has joined the chat")
        client_name_map[s] = packet["nick"]
        broadcast_message(create_json_join_packet(packet["nick"]), client_name_map)
    elif packet["type"] == "chat":
        print(f"{client_name_map[s]}: {packet['message']}")
        broadcast_message(create_client_chat_packet(packet["message"], client_name_map[s]), client_name_map)


def broadcast_message(message, client_name_map):
    print(message)
    for client_socket in client_name_map:
        try:
            client_socket.send(message.encode())
        except:
            print("Failed to send message to client socket {}".format(client_socket))
            print("Moving on to next client socket")


def create_client_chat_packet(message, nick):
    return json.dumps({"type": "chat", "message": message, "nick": nick})


def create_json_join_packet(client_name):
    return json.dumps({"type": "join", "nick": client_name})


def create_json_leave_packet(client_name):
    return json.dumps({"type": "leave", "nick": client_name})


def usage():
    print("usage: select_server.py port", file=sys.stderr)


def send_informational_message(client_socket, message):
    client_socket.send("*** ".encode() + message.encode())


def main(argv):
    try:
        port = int(argv[1])
    except:
        usage()
        return 1

    run_server(port)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
