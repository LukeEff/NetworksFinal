# Example usage:
#
# python select_client.py alice localhost 3490
# python select_client.py bob localhost 3490
# python select_client.py chris localhost 3490
#
# The first argument is a prefix that the server will print to make it
# easier to tell the different clients apart. You can put anything
# there.
import sys
import socket


def usage():
    print("usage: select_client.py prefix host port", file=sys.stderr)


def get_message_from_user(prefix):
    """ Returns a message from the user. """
    message = input(f"{prefix}> ")
    return message


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
    send_hello_packet(s, prefix)

    # Loop forever sending data at random time intervals
    while True:
        s.send(get_message_from_user(prefix).encode())


def send_hello_packet(s, prefix):
    s.send(prefix.encode())

if __name__ == "__main__":
    sys.exit(main(sys.argv))
