import socket
import threading
from .constants import *

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

def client_handler(client_socket):
    http_request = client_socket.recv(4096).decode()
    
    http_method, request_target = parse_request_lines(http_request)
    host, user_agent, accept = parse_headers(http_request)
    
    if request_target.startswith('/echo'):
        #Status line
        request_body = request_target.split('/')[2]
        
        msg = f'{http_version} {status_ok} {status_ok_text}\r\n'
        
        #Headers
        content_type = 'text/plain'
        content_length = len(request_body)
        
        msg += f'Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
        msg += f'{request_body}'
        
        client_socket.sendall(msg.encode())
        
    elif request_target.startswith('/user-agent'):
        msg = f'{http_version} {status_ok} {status_ok_text}\r\n'
        
        #Headers
        content_type = 'text/plain'
        content_length = len(user_agent)
        
        msg += f'Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
        msg += f'{user_agent}'
        
        client_socket.sendall(msg.encode())
    
    elif len(request_target.split('/')) == 2 and request_target.split('/')[1]:
        msg =  f'{http_version} {status_not_found} {status_not_found_text}\r\n\r\n'
        client_socket.sendall(msg.encode())
    
    else:
        msg = f'{http_version} {status_ok} {status_ok_text}\r\n\r\n'
        client_socket.sendall(msg.encode())  
    
    client_socket.close()

def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    while True:
        client_soc, client_address = server_socket.accept()
        threading.Thread(target=client_handler,args=(client_soc,), daemon=True).start()

if __name__ == "__main__":
    main()
