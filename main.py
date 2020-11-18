import os
from threading import Thread
from urllib.parse import unquote
from socket import socket, AF_INET, SOCK_STREAM, timeout

server_socket = socket(AF_INET, SOCK_STREAM)

server_socket.bind(('localhost', 8080))

server_socket.listen()
server_socket.settimeout(1)

STATIC_URL = 'static'
CHUNK_SIZE = 15000

def ext_content_type(data):
    content_type = "text/plain"

    if data.endswith(".json"):
        content_type = content_type = "text/json"
    elif data.endswith(".html") or data.endswith(".htm"):
        content_type = content_type = "text/html"
    elif data.endswith(".mp3"):
        content_type = content_type = "audio/mpeg"
    elif data.endswith(".wav"):
        content_type = content_type = "audio/wav"
    elif data.endswith(".mp4"):
        content_type = content_type = "video/mp4"
    elif data.endswith(".png"):
        content_type = content_type = "image/png"
    elif data.endswith(".gif"):
        content_type = content_type = "image/gif"
    elif data.endswith(".jpeg") or data.endswith(".jpg"):
        content_type = content_type = "image/jpeg"
    elif data.endswith(".pdf"):
        content_type = content_type = "application/pdf"
    
    return content_type

def join(a, b):
    return (a + "/" + b).replace('//', "/")

def encode_plain_file(socket, target, code=200, status="OK", args=None, content_type=None):
    content = ""
    with open(target, 'r', encoding="utf-8") as file:
        content += "\r\n".join(file.readlines())
    
    if args != None:
        for k, v in args.items():
            content = content.replace(k, v)

    msg = (
        f'HTTP/1.1 {code} {status}\r\n'
        'Date: Thu, 24 Sep 2020 21:00:15 GMT\r\n'
        "Server: Jimmy's/0.0.1 (Ubuntu)\r\n"
        f'Content-Type: {content_type if content_type != None else ext_content_type(target)}\r\n'
        f'Content-Length: {len(content.encode())}\r\n'
        '\r\n'
    )

    socket.send((msg + content).encode())

def encode_binary(socket, target, code=200, status="OK", content_type=None):
    content_type = content_type if content_type != None else ext_content_type(target)

    msg = (
        f'HTTP/1.1 {code} {status}\r\n'
        'Date: Thu, 24 Sep 2020 21:00:15 GMT\r\n'
        "Server: Jimmy's/0.0.1 (Ubuntu)\r\n"
        f'Content-Type: {content_type}\r\n'
        f'Content-Length: {os.path.getsize(target)}\r\n'
        '\r\n'
    )

    socket.send(msg.encode())


    with open(target, 'rb') as file:        
        while True:
            readed = file.read(CHUNK_SIZE)

            if readed: socket.send(readed)
            else: break

def is_binary(file_name):
    try:
        with open(file_name, 'tr') as check_file:  # try open file in text mode
            check_file.read()
            return False
    except:  # if fail then file is non-text (binary)
        return True

def generate_list(items):
    result = ""

    for name, uri, class_name in items:
        result += '<li><img src="/assets/{2}.png"><a href="{0}">{1}</a></li>'.format(name, uri, class_name)
    
    return result

def get_http_protocol(payload):
    rows = payload.split('\r\n')

    if len(rows) > 0:
        if len(rows[0].split(" ")) == 3:
            return tuple(rows[0].split(" "))
    
    return None

def process_request(client_socket, address_client):
    payload = client_socket.recv(2048).decode('ascii')
    presenting_protocol = get_http_protocol(payload)

    if presenting_protocol == None:
        encode_plain_file(client_socket, "bad_request.html", code=400, status="Bad request")
    
    method, url, version = presenting_protocol

    if not method.upper() in {'GET', 'PUT', 'POST', 'DELETE', 'PATCH'}:
        encode_plain_file(client_socket, "bad_request.html", code=400, status="Bad request")
    
    if not url.startswith("/"):
        encode_plain_file(client_socket, "bad_request.html", code=400, status="Bad request")

    if not ("HTTP/1.1" == version or "HTTP/1.0" == version):
        encode_plain_file(client_socket, "bad_request.html", code=505, status="HTTP Version Not Supported")

    # 
    url = unquote(url)
    target = join(STATIC_URL, url).replace("//", "/")
    print(target)

    # Is a folder
    if os.path.isdir(target):
        # Has a index file
        if os.path.isfile(join(target, "index.html")):
            encode_plain_file(client_socket, join(target, "index.html"))
        
        # Has a index file
        elif os.path.isfile(join(target, "index.htm")):
            encode_plain_file(client_socket, join(target, "index.htm"))

        # Return the list of files
        else:
            path = "/".join(url.split("/")[:-1])
            path = "/" if path == "" else path
            _, dirs, files = next(iter(os.walk(target)))

            list_itemns = (
                [ ( path, ".", "folder" ,) ]
                + [ ( join(url, d), d, "folder" ,) for d in dirs]
                + [ ( join(url, f), f, "document" ,) for f in files]
            )

            args = {
                "{{directory}}": url,
                "{{files}}": generate_list(list_itemns)
            }

            encode_plain_file(client_socket,"list_files.html", args=args)
    
    elif not os.path.isfile(target):
        encode_plain_file(client_socket, "not_found.html", code=404, status="Not found")

    else:
        if is_binary(target):
            encode_binary(client_socket, target)
        else:
            encode_plain_file(client_socket, target)
    
    client_socket.close()

while True:
    try:
        data = server_socket.accept()
    except timeout:
        continue

    Thread(target=process_request, args=data).start()
