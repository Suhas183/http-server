import socket
import threading
import argparse
import os
import gzip
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
    try:
        accept_encoding = headers.get('Accept-Encoding')
        if 'gzip' not in accept_encoding:
            accept_encoding = None
        else:
            accept_encoding = 'gzip'   
    except:
        accept_encoding = None        
       
    return host, user_agent, accept, accept_encoding

def parse_body(http_request):
    return http_request.split('\r\n')[-1]

def client_handler(client_socket, directory = None):
    http_request = client_socket.recv(4096).decode()
    
    http_method, request_target = parse_request_lines(http_request)
    host, user_agent, accept, accept_encoding = parse_headers(http_request)
    body = parse_body(http_request)
    
    if directory and http_method == 'POST':
        file_name = request_target.split('/')[2]
        with open(os.path.join(directory,file_name), "w") as file:
            file.write(body)
            
        msg = f'{http_version} {status_created} {status_created_text}\r\n\r\n'  
        
        client_socket.sendall(msg.encode())      
        
    elif directory and http_method == 'GET':    
        msg = f'{http_version} {status_ok} {status_ok_text}\r\n'
        #Headers
        content_type = 'application/octet-stream'
        content_length = 0
        content = ''
        
        try:
            file_name = request_target.split('/')[2]
            with open(os.path.join(directory,file_name), "r") as file:
                content = file.read()
                content_length = len(content)
        except FileNotFoundError:
            msg =  f'{http_version} {status_not_found} {status_not_found_text}\r\n\r\n'
            client_socket.sendall(msg.encode())
        
        if accept_encoding:
            msg += f'Content-Encoding: {accept_encoding}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
        else:
            msg += f'Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
                    
        msg += content
        client_socket.sendall(msg.encode())
        
    elif request_target.startswith('/echo'):
        #Status line
        request_body = request_target.split('/')[2]
        
        msg = f'{http_version} {status_ok} {status_ok_text}\r\n'
        
        #Headers
        content_type = 'text/plain'
        content_length = len(request_body)
        
        if accept_encoding:
            encoded_request_body = request_body.encode()
            gzip_compressed = gzip.compress(encoded_request_body)
            content_length = len(gzip_compressed)
            msg += f'Content-Encoding: {accept_encoding}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
            client_socket.sendall(msg.encode())
            client_socket.sendall(gzip_compressed)
        else:
            msg += f'Content-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
            msg += request_body
            client_socket.sendall(msg.encode())
        
    elif request_target.startswith('/user-agent'):
        msg = f'{http_version} {status_ok} {status_ok_text}\r\n'
        
        #Headers
        content_type = 'text/plain'
        content_length = len(user_agent)
        
        if accept_encoding:
            msg += f'Content-Encoding: {accept_encoding}\r\nContent-Type: {content_type}\r\nContent-Length: {content_length}\r\n\r\n'
        else:
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
            parser = argparse.ArgumentParser()
            parser.add_argument('--directory', default=None)
            args = parser.parse_args()
            directory = args.directory
            
            if directory:
                if not os.path.isdir(directory):
                    msg = f'{http_version} {status_ok} {status_ok_text}\r\n\r\n'
                    client_soc.sendall(msg.encode())
                    
                else:
                    threading.Thread(target=client_handler,args=(client_soc,directory,), daemon=True).start()
            
            else:
                threading.Thread(target=client_handler,args=(client_soc,), daemon=True).start()         
            

if __name__ == "__main__":
    main()
