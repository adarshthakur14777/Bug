import socket
import threading
import datetime

LISTEN_PORT = 80  # You can change this to 8080 or anything open
FORWARD_TO = ("127.0.0.1", 22)  # Forward to local SSH server

def handle_client(client_socket):
    try:
        request = client_socket.recv(1024)
        if b"Host:" in request:
            # Send welcome HTTP response similar to FN Network
            response = (
                "HTTP/1.1 101 <b><i><font color=\"green\">WELCOME TO FN NETWORK</font></i></b>\r\n"
                f"Date: {datetime.datetime.utcnow():%a, %d %b %Y %H:%M:%S GMT}\r\n"
                "Connection: upgrade\r\n"
                "Upgrade: websocket\r\n"
                "Server: cloudflare\r\n"
                "CF-RAY: 1234567890abcdef-BOM\r\n"
                "\r\n"
            )
            client_socket.sendall(response.encode())

            # Forward the connection to local SSH
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect(FORWARD_TO)

            # Start bi-directional forwarding
            threading.Thread(target=pipe, args=(client_socket, remote_socket)).start()
            threading.Thread(target=pipe, args=(remote_socket, client_socket)).start()
        else:
            client_socket.close()
    except Exception as e:
        client_socket.close()

def pipe(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(100)
    print(f"[+] SNI Proxy Listening on Port {LISTEN_PORT}")

    while True:
        client, addr = server.accept()
        print(f"[+] Connection from {addr[0]}")
        threading.Thread(target=handle_client, args=(client,)).start()

if __name__ == "__main__":
    start_server()
    
