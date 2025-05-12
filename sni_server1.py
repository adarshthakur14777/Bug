import socket
import ssl
import threading

# Configuration
SNI_HOST = 'fn.black.one'
SNI_PORT = 443
LOCAL_BIND_PORT = 1080  # Local port to expose tunnel
BUFFER_SIZE = 4096

def websocket_handshake(sock):
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {SNI_HOST}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: upgrade\r\n"
        f"User-Agent: SNIInjector/1.0\r\n"
        f"\r\n"
    )
    sock.sendall(handshake.encode())
    response = sock.recv(1024)
    return b"101 Switching Protocols" in response

def forward(src, dst):
    try:
        while True:
            data = src.recv(BUFFER_SIZE)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

def handle_client(client_socket):
    try:
        # Connect to SNI host with TLS
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        wrapped = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=SNI_HOST)
        wrapped.connect((SNI_HOST, SNI_PORT))

        if not websocket_handshake(wrapped):
            print("[!] WebSocket handshake failed.")
            client_socket.close()
            return

        print("[+] WebSocket tunnel established.")

        # Start bidirectional forwarding
        threading.Thread(target=forward, args=(client_socket, wrapped)).start()
        threading.Thread(target=forward, args=(wrapped, client_socket)).start()
    except Exception as e:
        print(f"[!] Connection failed: {e}")
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', LOCAL_BIND_PORT))
    server.listen(50)
    print(f"[+] SNI Tunnel running on port {LOCAL_BIND_PORT}...")

    while True:
        client, addr = server.accept()
        print(f"[+] New connection from {addr[0]}")
        threading.Thread(target=handle_client, args=(client,)).start()

start_server()
