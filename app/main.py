import socket  # noqa: F401

def parse_request_lines(http_request):
    http_request_line = http_request.split('\r\n')[0]
    http_method, request_target, _ = http_request_line.split(' ', 2)
    return http_method, request_target

def parse_headers(http_request):
    headers = {}
    lines = http_request.split('\r\n')
    for line in lines[1:]:
        if ': ' in line:
            key,value = line.split(': ')
            headers[key] = value
    
    host = headers.get('Host')
    user_agent = headers.get('User-Agent')
    accept = headers.get('Accept')
       
    return host, user_agent, accept

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, addr = server_socket.accept()
    http_request = client_socket.recv(4096).decode()
    
    http_method, request_target = parse_request_lines(http_request)
    host, user_agent, accept = parse_headers(http_request)
    
    msg = None
    
    if request_target == '/' or request_target is None:
        msg = 'HTTP/1.1 200 OK\r\n\r\n'
    
    else:
        msg = 'HTTP/1.1 404 Not Found\r\n\r\n'    
   
    encoded_string = msg.encode()
    client_socket.sendall(encoded_string)
    client_socket.close()
    server_socket.close()


if __name__ == "__main__":
    main()
