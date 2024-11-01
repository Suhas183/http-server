import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, addr = server_socket.accept()
    msg = 'HTTP/1.1 200 OK\r\n\r\n'
    encoded_string = msg.encode()
    client_socket.sendall(encoded_string)
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
